from pathlib import Path
from typing import List, Any
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
 
def create_index(documents: List[Document], index_dir: Path, embeddings: Any) -> FAISS:
    vs = FAISS.from_documents(documents, embeddings)
    index_dir.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(index_dir))
    return vs

def load_index(index_dir: Path, embeddings: Any) -> FAISS:
    return FAISS.load_local(str(index_dir), embeddings, allow_dangerous_deserialization=True)

def index_exists(index_dir: Path) -> bool:
    if not index_dir.exists():
        return False
    idx = index_dir / "index.faiss"
    pkl = index_dir / "index.pkl"
    return idx.exists() and pkl.exists()
