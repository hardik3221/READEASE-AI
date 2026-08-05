from groq import AsyncGroq
import os
from dotenv import load_dotenv, find_dotenv

# find_dotenv() automatically walks up your folder tree to find the .env file!
load_dotenv(find_dotenv())

# Initialize the Asynchronous client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
async def simplify_text(text: str, level: str = "medium") -> str:
    """
    Simplifies text based on requested complexity: 'simple', 'medium', or 'detailed'.
    Includes chunking to handle large PDF documents without crashing.
    """
    prompts = {
        "simple": "Explain this using very basic words, short sentences, and simple everyday analogies suitable for a 10-year-old.",
        "medium": "Simplify this text for a student. Keep key ideas clear and replace overly complex jargon.",
        "detailed": "Simplify the main ideas using clear bullet points and structural headings, but retain advanced academic concepts."
    }

    instruction = prompts.get(level, prompts["medium"])
    
    # STRICT System Prompt to kill conversational filler
    system_content = f"You are ReadEase AI, an expert accessibility assistant. {instruction} OUTPUT ONLY THE SIMPLIFIED TEXT. Do not include any conversational filler, greetings, or explanations."

    # --- CHUNKING LOGIC ---
    # Break massive documents into smaller chunks (approx 4000 chars) by paragraph
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

    # Stitch it all back together
    return "\n\n".join(simplified_chunks)


async def extract_vocabulary(text: str) -> str:
    """
    Extracts difficult words from the text along with simple definitions.
    """
    # For vocabulary, we only need to scan the first chunk of text 
    # to avoid pulling 50 words from a 40-page document.
    text_sample = text[:4000] 

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract 3 to 5 difficult or key vocabulary words from the following text. "
                    "For each word, give a simple definition and a short example sentence. "
                    "OUTPUT ONLY THE VOCABULARY FORMAT. Do not include greetings or filler."
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