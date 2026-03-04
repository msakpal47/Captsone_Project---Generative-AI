import hashlib
import os
from typing import List
import numpy as np
from .config import OPENAI_API_KEY, EMBEDDING_DIM, OPENAI_EMBEDDING_MODEL, USE_OPENAI_EMBEDDINGS
from openai import OpenAI


class EmbeddingModel:
    def embed(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_one(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


class HashEmbeddingModel(EmbeddingModel):
    def __init__(self, dim: int):
        self.dim = dim

    def embed(self, texts: List[str]) -> np.ndarray:
        arr = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            h = hashlib.sha256(t.encode("utf-8")).digest()
            vals = np.frombuffer(h, dtype=np.uint8).astype(np.float32)
            v = np.zeros(self.dim, dtype=np.float32)
            for j in range(self.dim):
                v[j] = vals[j % len(vals)] / 255.0
            n = np.linalg.norm(v)
            if n > 0:
                v = v / n
            arr[i] = v
        return arr


class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(self, model: str, fallback_dim: int):
        self.client = OpenAI(api_key=OPENAI_API_KEY or None)
        self.model = model
        self.fallback = HashEmbeddingModel(fallback_dim)

    def embed(self, texts: List[str]) -> np.ndarray:
        try:
            resp = self.client.embeddings.create(model=self.model, input=texts)
            vecs = [d.embedding for d in resp.data]
            arr = np.array(vecs, dtype=np.float32)
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return arr / norms
        except Exception:
            return self.fallback.embed(texts)


def load_embedding_model() -> EmbeddingModel:
    if OPENAI_API_KEY and str(USE_OPENAI_EMBEDDINGS) == "1":
        return OpenAIEmbeddingModel(OPENAI_EMBEDDING_MODEL, EMBEDDING_DIM)
    return HashEmbeddingModel(EMBEDDING_DIM)
