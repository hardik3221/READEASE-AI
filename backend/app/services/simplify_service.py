# app/services/simplify_service.py
import os
import google.generativeai as genai

# Set this in your terminal: export GEMINI_API_KEY="your_api_key_here"
# Or use python-dotenv to load it from a .env file
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    # Using flash for fast, cost-effective generation
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    model = None

def simplify_text_with_ai(raw_text: str) -> str:
    """Passes raw text to the LLM to rewrite it for accessibility."""
    if not model:
        # Fallback if no API key is set during testing
        return "⚠️ Setup missing: No AI API key found. Here is your text back:\n\n" + raw_text

    prompt = f"""
    You are an expert in accessible education for neurodivergent students. 
    Rewrite the following text to make it extremely easy to understand.
    
    Rules:
    - Use active voice and plain English.
    - Remove complex jargon or explain it simply.
    - Keep sentences short.
    - Do not use markdown bullet points or headers, just plain paragraph text.
    
    Text to simplify:
    {raw_text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"AI Generation failed: {str(e)}")