"""
AI Testing API Routes - For testing action item extraction
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..services.ai_processor_simple import AIProcessor


router = APIRouter()

# Global AI processor instance
ai_processor = None


class TestExtractionRequest(BaseModel):
    content: str = Field(..., description="Content to extract action items from")
    source_type: str = Field(
        "email", description="Type of source (email, meeting, chat)"
    )
    source_id: str = Field("test", description="Source identifier")


class TestExtractionResponse(BaseModel):
    status: str
    message: str
    action_items: List[Dict[str, Any]]
    processing_time_ms: Optional[float] = None
    content_length: int


class AIStatusResponse(BaseModel):
    ollama_status: str
    model_status: str
    available_models: List[str]
    target_model: str
    model_ready: bool
    processor_initialized: bool


async def get_ai_processor():
    """Get or initialize the AI processor"""
    global ai_processor
    if ai_processor is None:
        ai_processor = AIProcessor()
        await ai_processor.initialize()
    return ai_processor


@router.get("/status", response_model=AIStatusResponse)
async def ai_status():
    """Check AI processor and Ollama status"""
    try:
        processor = await get_ai_processor()
        test_result = processor.test_connection()

        return AIStatusResponse(
            ollama_status=test_result["status"],
            model_status=test_result["message"],
            available_models=test_result.get("available_models", []),
            target_model=test_result["target_model"],
            model_ready=test_result.get("model_ready", False),
            processor_initialized=processor.is_initialized,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to check AI status: {str(e)}"
        )


@router.post("/test-extraction", response_model=TestExtractionResponse)
async def test_extraction(request: TestExtractionRequest):
    """Test action item extraction with provided content"""
    try:
        processor = await get_ai_processor()

        if not processor.is_initialized:
            raise HTTPException(status_code=503, detail="AI processor not initialized")

        # Time the extraction
        import time

        start_time = time.time()

        action_items = await processor.extract_action_items(
            content=request.content,
            source_type=request.source_type,
            source_id=request.source_id,
        )

        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Convert action items to dict format
        items_dict = [
            {
                "task": item.task,
                "assignee": item.assignee,
                "deadline": item.deadline,
                "priority": item.priority,
                "confidence": item.confidence,
                "context": item.context,
                "source": item.source,
            }
            for item in action_items
        ]

        return TestExtractionResponse(
            status="success",
            message=f"Extracted {len(action_items)} action items",
            action_items=items_dict,
            processing_time_ms=processing_time,
            content_length=len(request.content),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/test-sample")
async def test_sample_extraction():
    """Test extraction with a predefined sample"""
    try:
        processor = await get_ai_processor()
        result = await processor.test_extraction()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample test failed: {str(e)}")


@router.get("/models")
async def list_models():
    """List available Ollama models"""
    try:
        processor = await get_ai_processor()
        test_result = processor.test_connection()

        return {
            "status": test_result["status"],
            "available_models": test_result.get("available_models", []),
            "current_model": test_result["target_model"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")
