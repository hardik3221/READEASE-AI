import asyncio
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
        # Run BOTH AI calls at the exact same time using asyncio.gather
        # This instantly cuts your processing time in half!
        simplified, vocab = await asyncio.gather(
            simplify_text(payload.text),
            extract_vocabulary(payload.text)
        )
        
        return {
            "simplified_text": simplified,
            "vocabulary": vocab
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))