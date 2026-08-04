# app/services/ai_service.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def simplify_text(text: str, level: str = "medium") -> str:
    """
    Simplifies text based on requested complexity: 'simple', 'medium', or 'detailed'.
    """
    prompts = {
        "simple": "Explain this using very basic words, short sentences, and simple everyday analogies suitable for a 10-year-old.",
        "medium": "Simplify this text for a student. Keep key ideas clear and replace overly complex jargon.",
        "detailed": "Simplify the main ideas using clear bullet points and structural headings, but retain advanced academic concepts."
    }

    instruction = prompts.get(level, prompts["medium"])

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": f"You are ReadEase AI, an expert accessibility assistant. {instruction}"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

def extract_vocabulary(text: str) -> str:
    """
    Extracts difficult words from the text along with simple definitions.
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract 3 to 5 difficult or key vocabulary words from the following text. "
                    "For each word, give a simple definition and a short example sentence."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content