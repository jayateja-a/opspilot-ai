import hashlib
import math
import re
import httpx
from .config import settings

DIMENSIONS = 1536

def demo_embedding(text: str) -> list[float]:
    """Stable lexical hashing, not a semantic model. No Python hash randomization."""
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        digest = hashlib.sha256(word.encode()).digest()
        vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0
    norm = math.sqrt(sum(v * v for v in vector))
    return [v / norm if norm else v for v in vector]

def model_id() -> str:
    return "demo-hash-v1" if settings.ai_mode == "demo" else settings.embedding_model + ":1536"

def embed(text: str) -> list[float]:
    if settings.ai_mode == "demo":
        return demo_embedding(text)
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY required in openai mode")
    with httpx.Client(timeout=40) as client:
        response = client.post("https://api.openai.com/v1/embeddings",
            headers={"Authorization": "Bearer " + settings.openai_api_key},
            json={"model": settings.embedding_model, "input": text, "dimensions": DIMENSIONS})
        response.raise_for_status()
        vector = response.json()["data"][0]["embedding"]
    if len(vector) != DIMENSIONS or not all(math.isfinite(x) for x in vector):
        raise ValueError("Invalid embedding dimensions or values")
    return vector
