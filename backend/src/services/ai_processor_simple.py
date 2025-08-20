"""
Simplified AI Processor for TaskHarvester - MVP Implementation
"""

import json
import re
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

import ollama
from ..utils.config import get_settings


@dataclass
class ActionItem:
    """Simple action item data class"""

    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "medium"
    confidence: float = 0.0
    context: str = ""
    source: str = ""


class AIProcessor:
    """Simplified AI processor for action item extraction using Ollama"""

    def __init__(self):
        self.settings = get_settings()
        self.model_name = self.settings.ollama_model
        self.confidence_threshold = self.settings.ai_confidence_threshold
        self.ollama_client = None
        self.is_initialized = False

    async def initialize(self):
        """Initialize the AI processor"""
        print("[AI] Initializing AI Processor...")

        try:
            # Initialize Ollama client
            self.ollama_client = ollama.Client(host=self.settings.ollama_host)

            # Test connection to Ollama
            try:
                models = self.ollama_client.list()
                model_names = [model["name"] for model in models["models"]]
                print(f"[INFO] Available models: {model_names}")

                # Check if our model is available
                model_available = self.model_name in model_names
                if not model_available:
                    print(
                        f"[WARNING] Model {self.model_name} not found. Available models: {model_names}"
                    )
                    print("[INFO] Make sure you run: ollama pull llama3.1:8b")
                    # Don't fail initialization, just warn

                self.is_initialized = True
                print("[SUCCESS] AI Processor initialized successfully")

            except Exception as e:
                print(f"[WARNING] Could not connect to Ollama: {e}")
                print("[INFO] Make sure Ollama is running: ollama serve")
                self.is_initialized = False

        except Exception as e:
            print(f"[ERROR] Failed to initialize AI Processor: {e}")
            self.is_initialized = False

    def _build_extraction_prompt(self, content: str, source_type: str = "email") -> str:
        """Build a focused prompt for action item extraction"""

        # Limit content length to prevent token overflow
        max_content_length = 1500
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""You are an expert assistant that extracts actionable tasks from business communications.

CONTENT TO ANALYZE ({source_type}):
{content}

TASK:
Extract specific, actionable tasks that someone needs to complete. Focus on:
- Clear actions with verbs (complete, send, review, schedule, etc.)
- Specific deliverables or deadlines mentioned  
- Tasks assigned to people (names or "you", "I", "we")

RULES:
- Only extract concrete, actionable tasks
- Ignore vague statements like "let's discuss" or "keep in touch"
- Include the responsible person if mentioned
- Note any deadlines or timeframes
- Rate your confidence (0.0 to 1.0)

OUTPUT FORMAT (valid JSON only):
{{
  "action_items": [
    {{
      "task": "Complete quarterly budget review",
      "assignee": "John Smith",
      "deadline": "2024-01-15",
      "priority": "high",
      "confidence": 0.9,
      "context": "Board meeting preparation"
    }}
  ]
}}

Extract action items (JSON only):"""

        return prompt

    async def extract_action_items(
        self, content: str, source_type: str = "email", source_id: str = ""
    ) -> List[ActionItem]:
        """Extract action items from content using Ollama"""

        if not self.is_initialized:
            print("[ERROR] AI Processor not initialized")
            return []

        if not content.strip():
            return []

        # Quick relevance check
        action_keywords = [
            "action required",
            "follow up",
            "deadline",
            "due date",
            "please",
            "need to",
            "should",
            "must",
            "will you",
            "can you",
            "todo",
            "task",
            "assignment",
            "complete",
            "deliver",
            "prepare",
            "schedule",
            "meeting",
            "review",
            "send",
            "submit",
            "finish",
            "update",
        ]

        content_lower = content.lower()
        keyword_count = sum(
            1 for keyword in action_keywords if keyword in content_lower
        )

        # Skip processing if content seems irrelevant
        if keyword_count == 0 and len(content.split()) > 50:
            print("[SKIP] Skipping content - no action keywords found")
            return []

        print(
            f"[PROCESS] Processing {source_type} content ({len(content)} chars, {keyword_count} action keywords)..."
        )

        try:
            # Build prompt
            prompt = self._build_extraction_prompt(content, source_type)

            # Call Ollama
            print("[AI] Calling Ollama for action item extraction...")
            response = self.ollama_client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "top_p": 0.9,
                    "num_predict": 500,  # Limit response length
                    "stop": ["\\n\\n"],  # Stop at double newline
                },
            )

            # Parse response
            action_items = self._parse_llm_response(
                response["response"], source_type, source_id
            )

            # Filter by confidence threshold
            filtered_items = [
                item
                for item in action_items
                if item.confidence >= self.confidence_threshold
            ]

            print(
                f"[SUCCESS] Extracted {len(filtered_items)} action items (from {len(action_items)} candidates)"
            )

            return filtered_items

        except Exception as e:
            print(f"[ERROR] Error extracting action items: {e}")
            return []

    def _parse_llm_response(
        self, response: str, source_type: str, source_id: str
    ) -> List[ActionItem]:
        """Parse the LLM response into ActionItem objects"""

        try:
            print(f"[PARSE] Parsing LLM response: {response[:200]}...")

            # Try to extract JSON from response
            # Look for JSON between { and }
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if not json_match:
                print("[ERROR] No JSON found in response")
                return []

            json_str = json_match.group()
            data = json.loads(json_str)

            action_items = []

            for item_data in data.get("action_items", []):
                # Validate required fields
                if not item_data.get("task"):
                    continue

                # Parse deadline
                deadline_str = item_data.get("deadline")
                if deadline_str and deadline_str != "null":
                    # Keep as string for now, could parse to datetime later
                    deadline = deadline_str
                else:
                    deadline = None

                # Create ActionItem
                action_item = ActionItem(
                    task=item_data.get("task", "").strip(),
                    assignee=item_data.get("assignee", "").strip() or None,
                    deadline=deadline,
                    priority=item_data.get("priority", "medium"),
                    confidence=float(item_data.get("confidence", 0.0)),
                    context=item_data.get("context", "").strip(),
                    source=f"{source_type}:{source_id}",
                )

                # Validate confidence score
                if 0.0 <= action_item.confidence <= 1.0 and action_item.task:
                    action_items.append(action_item)

            return action_items

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"[ERROR] Error parsing LLM response: {e}")
            print(f"Response was: {response}")
            return []

    def test_connection(self) -> Dict[str, any]:
        """Test the connection to Ollama"""
        try:
            if not self.ollama_client:
                return {"status": "error", "message": "Client not initialized"}

            # Try to list models
            models = self.ollama_client.list()
            model_names = [m.model for m in models.models]

            # Check if our model is available
            model_available = self.model_name in model_names

            return {
                "status": "success" if model_available else "warning",
                "message": f"Ollama connected. Model {self.model_name} {'available' if model_available else 'not found'}",
                "available_models": model_names,
                "target_model": self.model_name,
                "model_ready": model_available,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not connect to Ollama: {str(e)}",
                "target_model": self.model_name,
            }

    async def test_extraction(self, test_content: str = None) -> Dict[str, any]:
        """Test action item extraction with sample content"""

        if not test_content:
            test_content = """
            Hi team,
            
            Following up on our meeting yesterday. Here are the action items:
            
            1. John needs to complete the quarterly budget review by Friday, January 15th
            2. Sarah should send the updated project timeline to stakeholders by end of week
            3. Mike will schedule the client presentation for next Tuesday
            4. Please all review the document I shared and provide feedback
            
            Let me know if you have any questions.
            
            Best regards,
            Alex
            """

        try:
            action_items = await self.extract_action_items(
                test_content, "test_email", "test_001"
            )

            return {
                "status": "success",
                "message": f"Extracted {len(action_items)} action items",
                "action_items": [
                    {
                        "task": item.task,
                        "assignee": item.assignee,
                        "deadline": item.deadline,
                        "priority": item.priority,
                        "confidence": item.confidence,
                        "context": item.context,
                    }
                    for item in action_items
                ],
                "test_content_length": len(test_content),
            }

        except Exception as e:
            return {"status": "error", "message": f"Test extraction failed: {str(e)}"}
