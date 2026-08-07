import requests

from config import BACKEND_URL


def upload_pdf(filename, file_bytes):
    """Posts the PDF to the /upload endpoint. Returns the raw response;
    the caller checks status_code exactly as the original code did."""
    files = {"file": (filename, file_bytes, "application/pdf")}
    return requests.post(f"{BACKEND_URL}/upload", files=files)


def simplify_text_request(text):
    """Posts extracted text to the /simplify endpoint. Returns the raw response."""
    payload = {"text": text}
    return requests.post(f"{BACKEND_URL}/simplify", json=payload)