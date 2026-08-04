from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import simplify_text


router = APIRouter()


class TextRequest(BaseModel):
    text: str


@router.post("/simplify")
def simplify(request: TextRequest):

    result = simplify_text(request.text)

    return {
        "simplified_text": result
    }