# app/services/pdf_service.py
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a saved PDF file on disk."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        page_text = page.get_text()
        if page_text:
            text += page_text + "\n"
    doc.close()
    return text.strip()

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts text directly from PDF raw bytes in memory."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        page_text = page.get_text()
        if page_text:
            text += page_text + "\n"
    doc.close()
    return text.strip()