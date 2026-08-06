# app/utils.py
import re
import math

def apply_bionic_reading(text: str) -> str:
    """
    Parses text and bolds the first half of every word using Markdown 
    to create a Bionic Reading effect for neurodivergent readers.
    """
    def bold_word(match):
        word = match.group(0)
        # Skip very short formatting characters
        if len(word) == 1:
            return f"**{word}**"
        
        # Calculate the halfway point (rounding up for odd-length words)
        midpoint = math.ceil(len(word) / 2)
        
        first_half = word[:midpoint]
        second_half = word[midpoint:]
        
        return f"**{first_half}**{second_half}"

    # Regex finds all alphabetical words
    bionic_text = re.sub(r'\b[a-zA-Z]+\b', bold_word, text)
    return bionic_text


def apply_smart_chunking(text: str, sentences_per_chunk: int = 2) -> str:
    """
    Breaks a large block of text into smaller micro-paragraphs (1-2 sentences)
    to reduce cognitive load and prevent visual walls of text.
    """
    # Split the text by sentence-ending punctuation followed by a space or newline
    sentences = re.split(r'(?<=[.!?])[\s\n]+', text.strip())
    
    # Filter out any empty strings just in case
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    # Group the sentences into chunks of size `sentences_per_chunk`
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)
        
    # Join the chunks with double newlines to force paragraph breaks in Markdown/HTML
    return "\n\n".join(chunks)