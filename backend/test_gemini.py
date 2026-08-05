from groq import Groq

import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system", 
            "content": "You are an expert text simplifier for neurodivergent readers. Simplify the following text to an 8th-grade reading level. Break up long, complex sentences. OUTPUT ONLY THE SIMPLIFIED TEXT. Do not include any conversational filler, greetings, or explanations."
        },
        {
            "role": "user", 
            "content": text_to_simplify
        }
    ]
)

print(response.choices[0].message.content)