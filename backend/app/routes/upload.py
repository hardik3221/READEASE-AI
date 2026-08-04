from fastapi import APIRouter, UploadFile, File
import shutil

from app.services.pdf_service import extract_text_from_pdf


router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_path)

    return {
        "filename": file.filename,
        "text": text
    }