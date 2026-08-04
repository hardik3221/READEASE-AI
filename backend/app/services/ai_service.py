from groq import Groq
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def simplify_text(text: str):
    """
    Takes complicated text and returns a simpler version using Groq AI
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You simplify difficult text for students. "
                    "Make it easier to understand while keeping the meaning."
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