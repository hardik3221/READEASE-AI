# app/routes/simplify.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import simplify_text, extract_vocabulary

router = APIRouter()

class TextRequest(BaseModel):
    text: str
    level: Optional[str] = "medium"

@router.post("/simplify")
def simplify(request: TextRequest):
    try:
        result = simplify_text(request.text, level=request.level)
        return {"simplified_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vocabulary")
def vocabulary(request: TextRequest):
    try:
        result = extract_vocabulary(request.text)
        return {"vocabulary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))