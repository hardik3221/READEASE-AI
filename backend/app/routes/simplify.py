from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import simplify_text, extract_vocabulary

router = APIRouter()

class SimplifyPayload(BaseModel):
    text: str
    level: str = "medium"

@router.post("/simplify")
async def simplify_endpoint(payload: SimplifyPayload):
    try:
        # 1. Run the summarization
        simplified = await simplify_text(payload.text)
        
        # 2. Run the real vocabulary extraction
        vocab = await extract_vocabulary(payload.text)
        
        # 3. Return both to the frontend
        return {
            "simplified_text": simplified,
            "vocabulary": vocab
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))