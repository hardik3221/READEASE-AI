import os
import re
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from groq import AsyncGroq

# Multi-strategy .env loader
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv(find_dotenv())

# Global client cache
_client: AsyncGroq | None = None

def get_groq_client() -> AsyncGroq:
    """
    Lazy loader for AsyncGroq client. 
    Prevents server startup crashes by validating the key only when an API call is made.
    """
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing! Please ensure you have a .env file in your backend folder "
                "containing GROQ_API_KEY=gsk_your_key_here"
            )
        _client = AsyncGroq(api_key=api_key)
    return _client


def clean_for_tts(text: str) -> str:
    """
    Strips Markdown formatting (*, #, _, `, >) so Text-to-Speech engines 
    don't read out symbols like 'hashtag' or 'asterisk'.
    """
    text = re.sub(r'[\*\_`\#\>]', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # convert [text](link) to text
    return text.strip()


async def simplify_text(
    text: str, 
    level: str = "medium", 
    mode: str = "summary",
    tts_format: bool = False
) -> str:
    """
    Simplifies text based on requested target audience level and output mode.
    
    Levels:
    - 'child': Suitable for a 10-year-old / ESL beginner.
    - 'student': Clear explanations, replaces jargon, retains core ideas.
    - 'executive': High-level key takeaways for quick reading.
    - 'academic': Clear structure while retaining complex technical/academic context.
    
    Modes:
    - 'summary': High-level key takeaways and core narrative.
    - 'detailed': Section-by-section breakdown.
    - 'bullet_points': Actionable bulleted list.
    """
    client = get_groq_client()

    # Level-specific instructions
    level_prompts = {
        "child": "Explain this using very basic words, short sentences, and everyday analogies suitable for a 10-year-old.",
        "student": "Simplify this text for a high school or college student. Keep key ideas clear and replace complex jargon with plain terms.",
        "executive": "Tailor this for an executive. Focus strictly on business outcomes, key metrics, conclusions, and core takeaways.",
        "academic": "Maintain precision and advanced concepts, but reorganize and clarify dense academic jargon into accessible prose."
    }

    # Mode-specific instructions
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

    # --- ASYNC PROCESSING ---
    simplified_chunks = []
    for chunk in chunks:
        if not chunk.strip():
            continue
            
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": chunk}
            ],
            temperature=0.3
        )
        simplified_chunks.append(response.choices[0].message.content)

    output = "\n\n".join(simplified_chunks)

    # Clean Markdown if requested for TTS audio playback
    if tts_format:
        output = clean_for_tts(output)

    return output


async def extract_vocabulary(text: str) -> str:
    """
    Extracts difficult or key words from the text along with simple definitions and example sentences.
    """
    client = get_groq_client()
    text_sample = text[:4000] 

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract 3 to 5 key or difficult vocabulary words from the text. "
                    "For each word, format as:\n"
                    "• **[Word]**: [Simple Definition]\n  *Example*: [Short example sentence]\n\n"
                    "OUTPUT ONLY THE VOCABULARY LIST. No conversational greetings or intro."
                )
            },
            {
                "role": "user",
                "content": text_sample
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
async def extract_vocabulary(text: str) -> str:
    """
    Extracts 3 to 5 difficult vocabulary words with simple definitions.
    """
    if not text or not text.strip():
        return "No text available to extract vocabulary."

    client = get_groq_client()
    # Take the first 4000 characters to avoid overloading the context window
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
                {
                    "role": "user",
                    "content": text_sample
                }
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        return content if content else "AI returned an empty vocabulary list."
        
    except Exception as e:
        # If the API fails, this will print the exact error inside your Streamlit tab!
        return f"⚠️ **Could not generate vocabulary.**\n\nError details: `{str(e)}`"