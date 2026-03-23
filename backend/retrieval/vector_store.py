# vector_store.py

def simple_search(query, chunks, top_k=1):
    scores = []

    for chunk in chunks:
        score = sum(word in chunk.lower() for word in query.lower().split())
        scores.append(score)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

    return [chunk for chunk, _ in ranked[:top_k]]