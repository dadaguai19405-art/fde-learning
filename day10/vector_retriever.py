import hashlib
import math
import re


def tokenize(text):
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+", text)

    for chunk in re.findall(r"[\u4e00-\u9fff]+", text):
        tokens.extend(chunk)
        tokens.extend(
            chunk[index:index + 2]
            for index in range(len(chunk) - 1)
        )

    return tokens


def vectorize(text, dimensions=256):
    vector = [0.0] * dimensions

    for token in tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [value / norm for value in vector]


def cosine_similarity(left, right):
    return sum(
        left_value * right_value
        for left_value, right_value in zip(left, right)
    )


def retrieve_vector(query, documents, top_k=2):
    query_vector = vectorize(query)
    scored = []

    for document in documents:
        text = (
            f"{document['title']} {document['content']} "
            f"{' '.join(document['keywords'])}"
        )
        score = cosine_similarity(
            query_vector,
            vectorize(text),
        )

        if score > 0:
            scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [
        {"score": score, **document}
        for score, document in scored[:top_k]
    ]
