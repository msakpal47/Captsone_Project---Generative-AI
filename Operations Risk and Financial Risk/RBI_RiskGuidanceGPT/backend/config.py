from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

def _resolve_path(val: str) -> Path:
    p = Path(val)
    if not p.is_absolute():
        p = BASE_DIR / p
    return p

DATA_DIR = _resolve_path(os.getenv("DATA_DIR", "backend/data"))
INDEX_DIR = _resolve_path(os.getenv("INDEX_DIR", "backend/faiss_index"))

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
