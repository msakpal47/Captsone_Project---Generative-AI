from pathlib import Path
import re
import os
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from . import config
from .vector_store import create_index, load_index, index_exists
from pathlib import Path

class RAGPipeline:
    def __init__(self, data_dir: Path = config.DATA_DIR, index_dir: Path = config.INDEX_DIR):
        self.data_dir = Path(data_dir)
        self.index_dir = Path(index_dir)
        self.embeddings: Optional[object] = None
        self.vs = None
        self.last_index_info: Dict[str, Any] = {"indexed_chunks": 0, "documents_found": 0, "files": []}

    def ensure_embeddings(self):
        if self.embeddings is None:
            try:
                model_name = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
                self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
            except Exception:
                # last resort: local hash embeddings requiring no downloads
                from langchain_core.embeddings import Embeddings
                import math, re
                class LocalHashEmbeddings(Embeddings):
                    def __init__(self, dim: int = 384):
                        self.dim = dim
                    def _vec(self, text: str):
                        v = [0.0] * self.dim
                        for w in re.findall(r"\w+", (text or "").lower()):
                            idx = (hash(w) % self.dim)
                            v[idx] += 1.0
                        norm = math.sqrt(sum(x*x for x in v)) or 1.0
                        return [x / norm for x in v]
                    def embed_documents(self, texts: List[str]) -> List[List[float]]:
                        return [self._vec(t) for t in texts]
                    def embed_query(self, text: str) -> List[float]:
                        return self._vec(text)
                self.embeddings = LocalHashEmbeddings()
        return self.embeddings

    def load_documents(self) -> List[Document]:
        docs: List[Document] = []
        # Prefer configured DATA_DIR, but also scan project root recursively for PDFs
        search_dirs = []
        if self.data_dir.exists():
            search_dirs.append(self.data_dir)
        try:
            project_root = config.BASE_DIR
            if project_root.exists():
                search_dirs.append(project_root)
        except Exception:
            pass

        seen = set()
        for ddir in search_dirs:
            for p in Path(ddir).rglob("*.pdf"):
                key = p.resolve()
                if key in seen:
                    continue
                seen.add(key)
                loaded_pages: List[Document] = []
                # try with PyPDF first
                try:
                    loader = PyPDFLoader(str(p))
                    loaded_pages = loader.load()
                except Exception:
                    loaded_pages = []
                # if empty content, fallback to pdfplumber extraction
                has_text = any((getattr(d, "page_content", "") or "").strip() for d in loaded_pages)
                if not loaded_pages or not has_text:
                    try:
                        import pdfplumber
                        with pdfplumber.open(str(p)) as pdf:
                            for i, page in enumerate(pdf.pages):
                                text = page.extract_text() or ""
                                text = text.strip()
                                if text:
                                    loaded_pages.append(Document(page_content=text, metadata={"source": str(p.name), "page": i}))
                    except Exception:
                        pass
                # final fallback: placeholder doc so index can be built
                if not loaded_pages:
                    placeholder = f"No extractable text found in {p.name}. Refer to the PDF directly."
                    loaded_pages.append(Document(page_content=placeholder, metadata={"source": str(p.name), "page": 0}))
                # attach metadata and collect
                for d in loaded_pages:
                    d.metadata = d.metadata or {}
                    try:
                        src_val = d.metadata.get("source")
                        src_name = Path(str(src_val or p.name)).name
                        d.metadata["source"] = src_name
                    except Exception:
                        d.metadata["source"] = str(p.name)
                docs.extend(loaded_pages)
        return docs

    def split_documents(self, docs: List[Document]) -> List[Document]:
        if not docs:
            return []
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        return splitter.split_documents(docs)

    def ingest(self) -> Dict[str, Any]:
        config.ensure_dirs()
        docs = self.load_documents()
        sources = sorted({d.metadata.get("source") for d in docs if d.metadata and d.metadata.get("source")})
        chunks = self.split_documents(docs)
        if not chunks:
            self.vs = None
            self.last_index_info = {"indexed_chunks": 0, "documents_found": len(sources), "files": sources, "message": "no_chunks"}
            return self.last_index_info
        try:
            embeddings = self.ensure_embeddings()
            self.vs = create_index(chunks, self.index_dir, embeddings)
            self.last_index_info = {"indexed_chunks": len(chunks), "documents_found": len(sources), "files": sources}
            return self.last_index_info
        except Exception as e:
            self.vs = None
            self.last_index_info = {"indexed_chunks": 0, "documents_found": len(sources), "files": sources, "message": str(e)[:200]}
            return self.last_index_info

    def load_or_ingest(self) -> None:
        config.ensure_dirs()
        try:
            if index_exists(self.index_dir):
                embeddings = self.ensure_embeddings()
                self.vs = load_index(self.index_dir, embeddings)
            else:
                self.ingest()
        except Exception:
            self.vs = None

    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        if not self.vs:
            return []
        docs = self.vs.similarity_search(query, k=max(k, 8))
        return docs[:k]

    def answer(self, query: str, k: int = 4) -> Dict[str, Any]:
        docs = self.retrieve(query, k=k)
        if not docs:
            return {"answer": "Not found in RBI guidelines.", "sources": []}
        context = "\n\n".join([d.page_content for d in docs])
        text = context[:2000]
        items = [s.strip() for s in re.split(r"(?<=[\.\!\?])\s+", text) if s.strip()]
        items = items[:12]
        lines = ["• " + s for s in items]
        formatted = "Answer\n" + "\n".join(lines)
        resp = type("R", (), {"content": formatted})
        sources = []
        for d in docs:
            src = d.metadata.get("source")
            page = d.metadata.get("page")
            sources.append({"source": src, "page": page})
        return {"answer": resp.content if hasattr(resp, 'content') else str(resp), "sources": sources}
