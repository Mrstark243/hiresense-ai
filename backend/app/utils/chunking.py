import re

def semantic_chunking(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    """
    Splits text into chunks based on character count with overlap, 
    attempting to keep sentences intact.
    """
    if not text:
        return []

    # Split by sentences (basic)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Handle sentences longer than chunk_size
            if len(sentence) > chunk_size:
                # Force split long sentence
                for i in range(0, len(sentence), chunk_size - overlap):
                    chunks.append(sentence[i:i + chunk_size].strip())
                current_chunk = ""
            else:
                current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    # Add overlap if possible (simplified here)
    return chunks
