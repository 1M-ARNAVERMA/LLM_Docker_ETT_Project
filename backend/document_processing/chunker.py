# chunker.py

def chunk_text(text, chunk_size=50, overlap=10):

    words = text.split()
    chunks = []

    step = chunk_size - overlap

    # safety check
    if step <= 0:
        step = chunk_size

    for i in range(0, len(words), step):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))

    return chunks