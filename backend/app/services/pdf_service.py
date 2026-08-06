import fitz  # PyMuPDF
import base64
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from groq import Groq

# Load environment variables
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv(find_dotenv())

# Global lazy-loaded client
_groq_client = None

def get_groq_client() -> Groq:
    """
    Lazy loader for Groq client to prevent startup crashes.
    """
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing! Ensure you have a .env file in your backend folder "
                "containing GROQ_API_KEY=gsk_your_key_here"
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts digital text via PyMuPDF. 
    If a page is scanned (< 50 chars), it calls Groq Vision for zero-dependency OCR.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()

        # If digital text extraction finds less than 50 characters, use AI Vision
        if len(text) < 50:
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode('utf-8')

            client = get_groq_client()

            vision_completion = client.chat.completions.create(
                model="qwen/qwen3.6-27b",  # <-- UPDATED TO ACTIVE VISION MODEL
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all readable text from this image accurately. Output ONLY the extracted text, no explanations."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1
            )
            text = vision_completion.choices[0].message.content.strip()

        if text:
            full_text.append(f"--- Page {page_num + 1} ---\n{text}")

    doc.close()
    
    extracted_full = "\n\n".join(full_text).strip()
    if not extracted_full:
        raise ValueError("Could not extract any readable text from this PDF.")

    return extracted_full