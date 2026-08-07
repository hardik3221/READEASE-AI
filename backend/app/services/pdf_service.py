import fitz  # PyMuPDF
import base64
import os
import itertools
import asyncio
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from groq import AsyncGroq

# Load environment variables
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv(find_dotenv())

# --- KEY POOLING SETUP (Dynamic for 7+ Keys) ---
api_keys = [os.getenv(f"GROQ_API_KEY_{i}") for i in range(1, 8)]
valid_keys = [k for k in api_keys if k and k.strip()]

if not valid_keys:
    raise RuntimeError("No GROQ API keys found! Add GROQ_API_KEY_1 through 7 to your .env file.")

key_cycle = itertools.cycle(valid_keys)

def get_async_groq_client() -> AsyncGroq:
    """Grabs the next key in line instantly for parallel distribution."""
    current_key = next(key_cycle)
    return AsyncGroq(api_key=current_key)

ocr_semaphore = asyncio.Semaphore(len(valid_keys))

async def ocr_page_async(page_num: int, base64_image: str) -> str:
    """Processes a single scanned page via async Vision AI."""
    async with ocr_semaphore:
        for attempt in range(3):
            client = get_async_groq_client()
            try:
                vision_completion = await client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
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
                return f"--- Page {page_num + 1} ---\n{text}"
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "rate_limit" in error_msg.lower():
                    print(f"⚠️ Vision Rate Limit on Page {page_num + 1}. Pausing 3s...")
                    await asyncio.sleep(3)
                else:
                    return f"--- Page {page_num + 1} ---\n[OCR Error: {error_msg}]"
        
        return f"--- Page {page_num + 1} ---\n[OCR Failed due to Rate Limits]"

async def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts text instantly. Sends scanned pages to Vision OCR in parallel."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    page_results = [None] * len(doc)
    ocr_tasks = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()

        if len(text) < 50:
            pix = page.get_pixmap(dpi=72)
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            ocr_tasks.append((page_num, ocr_page_async(page_num, base64_image)))
        else:
            page_results[page_num] = f"--- Page {page_num + 1} ---\n{text}"

    doc.close()

    if ocr_tasks:
        tasks = [task_data[1] for task_data in ocr_tasks]
        results = await asyncio.gather(*tasks)
        
        for i, (page_num, _) in enumerate(ocr_tasks):
            page_results[page_num] = results[i]

    extracted_full = "\n\n".join(filter(None, page_results)).strip()
    if not extracted_full:
        raise ValueError("Could not extract any readable text from this PDF.")

    return extracted_full