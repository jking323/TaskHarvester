"""
AI Processor Service - Core action item extraction using local LLM
"""
import json
import hashlib
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta

import ollama
import spacy
from sentence_transformers import SentenceTransformer

from ..models.action_item import ActionItem, ActionItemCreate
from ..utils.cache import CacheManager
from ..utils.config import get_settings


class AIProcessor:
    """Main AI processing service for action item extraction"""
    
    def __init__(self):
        self.settings = get_settings()
        self.cache = CacheManager()
        self.ollama_client = None
        self.nlp = None
        self.sentence_model = None
        self.confidence_threshold = 0.7
        
    async def initialize(self):
        """Initialize AI models"""
        print("[AI] Initializing AI models...")
        
        try:
            # Initialize Ollama client
            self.ollama_client = ollama.Client()
            
            # Pull Llama model if not exists
            try:
                self.ollama_client.show('llama3.1:8b')
            except:
                print("[DOWNLOAD] Downloading Llama 3.1 8B model (this may take a while)...")
                self.ollama_client.pull('llama3.1:8b')
            
            # Load spaCy model for NER
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("[ERROR] spaCy model not found. Run: python -m spacy download en_core_web_sm")
                raise
            
            # Load sentence transformer for similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            print("[SUCCESS] AI models initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize AI models: {e}")
            raise
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content caching"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _classify_relevance(self, content: str, source_type: str) -> float:
        """Classify if content contains actionable items"""
        
        # Quick keyword-based pre-filtering
        action_keywords = [
            'action required', 'follow up', 'deadline', 'due date',
            'please', 'need to', 'should', 'must', 'will you',
            'can you', 'todo', 'task', 'assignment', 'complete',
            'deliver', 'prepare', 'schedule', 'meeting'
        ]
        
        content_lower = content.lower()
        keyword_score = sum(1 for keyword in action_keywords if keyword in content_lower)
        
        # Normalize score (0-1)
        relevance_score = min(keyword_score / 5.0, 1.0)
        
        # Boost score for certain source types
        if source_type == 'meeting_transcript':
            relevance_score = min(relevance_score * 1.2, 1.0)
        
        return relevance_score
    
    def _extract_entities(self, text: str) -> Dict:
        """Extract entities using spaCy NER"""
        doc = self.nlp(text)
        
        entities = {
            'people': [],
            'dates': [],
            'organizations': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                entities['people'].append(ent.text)
            elif ent.label_ in ['DATE', 'TIME']:
                entities['dates'].append(ent.text)
            elif ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
        
        return entities
    
    def _parse_deadline(self, deadline_text: str) -> Optional[datetime]:
        """Parse deadline from extracted date text"""
        if not deadline_text:
            return None
            
        # Simple date parsing - could be enhanced with dateutil
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(\d{4}-\d{2}-\d{2})',      # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, deadline_text)
            if match:
                try:
                    date_str = match.group(1)
                    return datetime.strptime(date_str, '%m/%d/%Y' if '/' in date_str else '%Y-%m-%d')
                except ValueError:
                    continue
        
        # Relative dates
        if 'tomorrow' in deadline_text.lower():
            return datetime.now() + timedelta(days=1)
        elif 'next week' in deadline_text.lower():
            return datetime.now() + timedelta(weeks=1)
        
        return None
    
    async def extract_action_items(self, content: str, source_type: str, source_id: str) -> List[ActionItemCreate]:
        """Main method to extract action items from content"""
        
        # Check cache first
        content_hash = self._generate_content_hash(content)
        cached_result = self.cache.get_model_output(content_hash)
        if cached_result:
            return cached_result
        
        # Check relevance
        relevance = self._classify_relevance(content, source_type)
        if relevance < 0.3:
            return []
        
        # Extract entities
        entities = self._extract_entities(content)
        
        # Prepare prompt for LLM
        prompt = self._build_extraction_prompt(content, source_type, entities)
        
        try:
            # Call Ollama
            response = self.ollama_client.generate(
                model='llama3.1:8b',
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for consistent extraction
                    'top_p': 0.9,
                    'num_predict': 1000
                }
            )
            
            # Parse LLM response
            action_items = self._parse_llm_response(response['response'], entities)
            
            # Filter by confidence
            filtered_items = [item for item in action_items if item.confidence >= self.confidence_threshold]
            
            # Cache result
            self.cache.cache_model_output(content_hash, filtered_items)
            
            return filtered_items
            
        except Exception as e:
            print(f"[ERROR] Error in action item extraction: {e}")
            return []
    
    def _build_extraction_prompt(self, content: str, source_type: str, entities: Dict) -> str:
        """Build the extraction prompt for the LLM"""
        
        prompt = f"""
EXTRACT ACTION ITEMS FROM: {source_type.upper()}

CONTENT:
{content[:2000]}  # Limit content length

INSTRUCTIONS:
You are an expert at identifying actionable tasks from business communications.
Extract specific, actionable tasks that someone needs to complete.

CRITERIA FOR ACTION ITEMS:
- Must be specific and actionable
- Must have a clear owner (person responsible)
- Should have a timeframe if mentioned
- Ignore vague statements like "let's discuss"

DETECTED ENTITIES:
People: {', '.join(entities.get('people', []))}
Dates: {', '.join(entities.get('dates', []))}

OUTPUT FORMAT (JSON):
{{
  "action_items": [
    {{
      "task": "Complete the quarterly report",
      "assignee": "John Smith",
      "deadline": "2024-01-15",
      "priority": "high",
      "confidence": 0.9,
      "context": "Board meeting preparation"
    }}
  ]
}}

Rules:
- Only include tasks with confidence >= 0.7
- Use person names from detected entities when possible
- Priority: high/medium/low
- Deadline format: YYYY-MM-DD or null
- Context: brief explanation of why this is a task

Extract action items:
"""
        return prompt
    
    def _parse_llm_response(self, response: str, entities: Dict) -> List[ActionItemCreate]:
        """Parse the LLM response into ActionItem objects"""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return []
            
            data = json.loads(json_match.group())
            action_items = []
            
            for item_data in data.get('action_items', []):
                # Parse deadline
                deadline = None
                if item_data.get('deadline'):
                    deadline = self._parse_deadline(item_data['deadline'])
                
                # Create ActionItemCreate object
                action_item = ActionItemCreate(
                    task_description=item_data.get('task', ''),
                    assignee_email=self._resolve_assignee_email(item_data.get('assignee', '')),
                    deadline=deadline,
                    priority=item_data.get('priority', 'medium'),
                    confidence_score=float(item_data.get('confidence', 0.0)),
                    context=item_data.get('context', '')
                )
                
                if action_item.task_description and action_item.confidence_score >= self.confidence_threshold:
                    action_items.append(action_item)
            
            return action_items
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"[ERROR] Error parsing LLM response: {e}")
            return []
    
    def _resolve_assignee_email(self, assignee_name: str) -> Optional[str]:
        """Resolve assignee name to email address"""
        # TODO: Implement user mapping lookup
        # For now, return the name as-is
        return assignee_name if assignee_name else None
    
    async def check_duplicate(self, new_item: ActionItemCreate, existing_items: List[ActionItem]) -> bool:
        """Check if action item is a duplicate using semantic similarity"""
        
        if not existing_items:
            return False
        
        # Get embeddings for new item
        new_embedding = self.sentence_model.encode([new_item.task_description])
        
        # Check against existing items
        for existing in existing_items:
            existing_embedding = self.sentence_model.encode([existing.task_description])
            
            # Calculate cosine similarity
            similarity = self.sentence_model.similarity(new_embedding, existing_embedding)[0][0]
            
            # If similarity > threshold and same assignee, likely duplicate
            if similarity > 0.8 and new_item.assignee_email == existing.assignee_email:
                return True
        
        return False