def simple_search(query, chunks, top_k=1):

    query_words = [w for w in query.lower().split() if w not in ["what", "is", "the", "a", "an"]]

    scores = []

    for chunk in chunks:
        score = sum(word in chunk.lower() for word in query_words)
        scores.append(score)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

    return [chunk for chunk, score in ranked[:top_k] if score > 0]