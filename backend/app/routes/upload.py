# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import extract_text_from_pdf_bytes

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        pdf_bytes = await file.read()
        
        # 🚨 THE FIX: You MUST have 'await' right here because the PDF service is now async!
        text = await extract_text_from_pdf_bytes(pdf_bytes)
        
        if not text:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text. The PDF might be scanned or image-only."
            )

        return {
            "filename": file.filename,
            "text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")