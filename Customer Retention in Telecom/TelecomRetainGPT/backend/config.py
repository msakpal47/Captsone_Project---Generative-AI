import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(str(ENV_PATH))
else:
    load_dotenv()

def _fallback(val: str | None, default: str) -> str:
    if val is None:
        return default
    if isinstance(val, str) and val.strip() == "":
        return default
    return val

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = _fallback(os.getenv("LLM_MODEL"), "gpt-3.5-turbo")
EMBEDDING_DIM = int(_fallback(os.getenv("EMBEDDING_DIM"), "256"))
# Store vectors outside backend to avoid dev server reloads on index writes
VECTOR_DIR = _fallback(os.getenv("VECTOR_DIR"), str(BASE_DIR / "storage" / "vector_data"))
DATA_DIR = _fallback(os.getenv("DATA_DIR"), str(BASE_DIR / "backend" / "data"))
TOP_K = int(_fallback(os.getenv("TOP_K"), "4"))
APP_HOST = _fallback(os.getenv("APP_HOST"), "0.0.0.0")
APP_PORT = int(_fallback(os.getenv("APP_PORT"), "8000"))
USE_OPENAI_EMBEDDINGS = _fallback(os.getenv("USE_OPENAI_EMBEDDINGS"), "0")
USE_OPENAI_CHAT = _fallback(os.getenv("USE_OPENAI_CHAT"), "0")
OPENAI_EMBEDDING_MODEL = _fallback(os.getenv("OPENAI_EMBEDDING_MODEL"), "text-embedding-3-small")
CHUNK_SIZE = int(_fallback(os.getenv("CHUNK_SIZE"), "300"))
CHUNK_OVERLAP = int(_fallback(os.getenv("CHUNK_OVERLAP"), "50"))
