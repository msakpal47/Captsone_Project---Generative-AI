from typing import Any
from backend.config import create_embeddings


def get_embeddings() -> Any:
    return create_embeddings()
