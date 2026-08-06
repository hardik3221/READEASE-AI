# app/routes/history.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import (
    save_document,
    get_all_documents,
    get_document_by_id,
    delete_document
)

router = APIRouter(prefix="/history", tags=["History"])

class SaveDocumentRequest(BaseModel):
    filename: str
    original_text: str
    simplified_text: str

@router.post("")
async def create_history_entry(data: SaveDocumentRequest):
    """Saves a document and its simplified output into history."""
    try:
        doc_id = save_document(data.filename, data.original_text, data.simplified_text)
        return {
            "message": "Document history saved successfully",
            "id": doc_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save history: {str(e)}")

@router.get("")
async def fetch_all_history():
    """Retrieves all document history items."""
    try:
        documents = get_all_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@router.get("/{doc_id}")
async def fetch_history_by_id(doc_id: int):
    """Retrieves a specific document history item by ID."""
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document history record not found.")
    return doc

@router.delete("/{doc_id}")
async def remove_history_entry(doc_id: int):
    """Deletes a history item by ID."""
    success = delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document history record not found or already deleted.")
    return {"message": f"Document entry {doc_id} deleted successfully"}