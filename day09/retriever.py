from day09.knowledge_base import DOCUMENTS


def retrieve(query, top_k=2):
    query = query.lower()
    scored = []

    for document in DOCUMENTS:
        score = 0

        for keyword in document["keywords"]:
            if keyword.lower() in query:
                score += 2

        if document["title"].lower() in query:
            score += 3

        if score > 0:
            scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [document for _, document in scored[:top_k]]
