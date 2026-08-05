from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import simplify_text, extract_vocabulary

router = APIRouter()

class TextRequest(BaseModel):
    text: str
    level: Optional[str] = "medium"

@router.post("/simplify")
async def simplify(request: TextRequest): # Added async
    try:
        # Added await
        result = await simplify_text(request.text, level=request.level) 
        return {"simplified_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vocabulary")
async def vocabulary(request: TextRequest): # Added async
    try:
        # Added await
        result = await extract_vocabulary(request.text) 
        return {"vocabulary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))