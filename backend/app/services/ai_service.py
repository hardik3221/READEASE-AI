import os
import re
import asyncio
import itertools
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from groq import AsyncGroq

# Multi-strategy .env loader
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

def get_groq_client() -> AsyncGroq:
    """Grabs the next key in the rotation line and creates a fresh client."""
    current_key = next(key_cycle)
    return AsyncGroq(api_key=current_key)

def clean_for_tts(text: str) -> str:
    text = re.sub(r'[\*\_`\#\>]', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()

# 🚨 Set concurrency to exactly match your number of keys (7)
MAX_CONCURRENT_REQUESTS = len(valid_keys)
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def process_chunk(chunk: str, system_content: str, retries=3) -> str:
    """Helper function to process a single chunk safely in parallel."""
    async with semaphore:
        for attempt in range(retries):
            # Grabs a fresh key for this specific chunk
            client = get_groq_client()
            try:
                response = await client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": chunk}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "rate_limit" in error_msg:
                    print(f"⚠️ Groq Rate Limit hit. Rotating key and pausing 3s... (Attempt {attempt + 1} of {retries})")
                    await asyncio.sleep(3)
                else:
                    return f"\n[Error processing chunk: {error_msg}]\n"
        
        return "\n[Chunk failed after multiple retries due to API rate limits.]\n"

async def simplify_text(text: str, level: str = "medium", mode: str = "summary", tts_format: bool = False) -> str:
    level_prompts = {
        "child": "Explain this using very basic words, short sentences, and everyday analogies suitable for a 10-year-old.",
        "student": "Simplify this text for a high school or college student. Keep key ideas clear and replace complex jargon with plain terms.",
        "executive": "Tailor this for an executive. Focus strictly on business outcomes, key metrics, conclusions, and core takeaways.",
        "academic": "Maintain precision and advanced concepts, but reorganize and clarify dense academic jargon into accessible prose."
    }
    mode_prompts = {
        "summary": "Provide a cohesive, easily digestible summary of the main narrative.",
        "detailed": "Provide a comprehensive section-by-section breakdown with structural headings.",
        "bullet_points": "Extract all critical points into clear, prioritized bullet points."
    }

    instruction_level = level_prompts.get(level, level_prompts["student"])
    instruction_mode = mode_prompts.get(mode, mode_prompts["summary"])

    system_content = (
        f"You are ReadEase AI, an expert accessibility and reading assistant.\n"
        f"Target Audience Instruction: {instruction_level}\n"
        f"Format Instruction: {instruction_mode}\n"
        "STRICT RULE: OUTPUT ONLY THE SIMPLIFIED TEXT. Do not include conversational greetings, intros, or introspective comments."
    )

    # --- CHUNKING LOGIC ---
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < 4000:
            current_chunk += p + "\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = p + "\n"
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # --- PARALLEL ASYNC PROCESSING ---
    tasks = [process_chunk(chunk, system_content) for chunk in chunks if chunk.strip()]
    simplified_chunks = await asyncio.gather(*tasks)

    output = "\n\n".join(filter(None, simplified_chunks))

    if tts_format:
        output = clean_for_tts(output)

    return output

async def extract_vocabulary(text: str) -> str:
    """Extracts 3 to 5 difficult vocabulary words with simple definitions."""
    if not text or not text.strip():
        return "No text available to extract vocabulary."

    client = get_groq_client()
    text_sample = text[:4000]

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract 3 to 5 difficult or key vocabulary words from the following text. "
                        "For each word, give a simple definition and a short example sentence. "
                        "Format each item nicely using bullet points.\n"
                        "OUTPUT ONLY THE VOCABULARY LIST. Do not include greetings or conversational filler."
                    )
                },
                {"role": "user", "content": text_sample}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        return content if content else "AI returned an empty vocabulary list."
        
    except Exception as e:
        return f"⚠️ **Could not generate vocabulary.**\n\nError details: `{str(e)}`"