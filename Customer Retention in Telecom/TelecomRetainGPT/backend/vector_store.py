import json
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import numpy as np
try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    faiss = None  # type: ignore
    _HAS_FAISS = False
from pypdf import PdfReader
try:
    from pdfminer.high_level import extract_text as pdfminer_extract
    _HAS_PDFMINER = True
except Exception:
    _HAS_PDFMINER = False
try:
    from docx import Document  # python-docx
    _HAS_DOCX = True
except Exception:
    _HAS_DOCX = False
try:
    import pytesseract  # type: ignore
    from pdf2image import convert_from_path  # type: ignore
    from PIL import Image  # type: ignore
    _HAS_OCR = True
except Exception:
    _HAS_OCR = False
from .embeddings import load_embedding_model
from .config import VECTOR_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


class VectorStore:
    def __init__(self):
        self.dim = None
        self.index = None
        self.emb = load_embedding_model()
        self.meta: List[Dict[str, Any]] = []

    def _pdf_text(self, f: Path) -> str:
        # Try PyPDF first
        content = ""
        try:
            reader = PdfReader(str(f))
            pages = [page.extract_text() or "" for page in reader.pages]
            content = "\n".join(pages)
        except Exception:
            content = ""
        # Fallback to pdfminer if short
        if len(content.strip()) < 200 and _HAS_PDFMINER:
            try:
                content = pdfminer_extract(str(f)) or ""
            except Exception:
                pass
        # Optional OCR if still empty and stack available
        if len(content.strip()) < 200 and _HAS_OCR:
            try:
                images = convert_from_path(str(f))
                ocr_texts = []
                for img in images:
                    txt = pytesseract.image_to_string(img)
                    if txt:
                        ocr_texts.append(txt)
                content = "\n".join(ocr_texts)
            except Exception:
                pass
        return content

    def _docx_text(self, f: Path) -> str:
        if not _HAS_DOCX:
            return ""
        try:
            doc = Document(str(f))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""

    def _txt_text(self, f: Path) -> str:
        try:
            return f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def build_from_pdfs(self, data_dir: str) -> Tuple[int, int]:
        texts: List[str] = []
        sources: List[str] = []
        base = Path(__file__).resolve().parent.parent
        candidates = []
        p = Path(data_dir)
        if p.exists():
            candidates.append(p)
        # Also look in backend root and project root for convenience
        candidates.append(base / "backend" / "data")
        candidates.append(base)
        candidates.append(base.parent)
        seen: set[str] = set()
        for dirp in candidates:
            if not dirp.exists():
                continue
            # Collect multiple file types
            for f in list(dirp.glob("*.pdf")) + list(dirp.glob("*.docx")) + list(dirp.glob("*.txt")):
                fp = str(f.resolve())
                if fp in seen:
                    continue
                seen.add(fp)
                content = ""
                if f.suffix.lower() == ".pdf":
                    content = self._pdf_text(f)
                elif f.suffix.lower() == ".docx":
                    content = self._docx_text(f)
                elif f.suffix.lower() == ".txt":
                    content = self._txt_text(f)
                content = (content or "").strip()
                if not content:
                    continue
                for ch in chunk_text(content):
                    texts.append(ch)
                    sources.append(str(f.name))
        if not texts:
            return 0, 0
        vecs = self.emb.embed(texts)
        self.dim = vecs.shape[1]
        if _HAS_FAISS:
            self.index = faiss.IndexFlatIP(self.dim)
        else:
            self.index = None
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vecs = vecs / norms
        if _HAS_FAISS:
            self.index.add(vecs.astype(np.float32))
        else:
            self._fallback_matrix = vecs.astype(np.float32)
        self.meta = [{"text": t, "source": s} for t, s in zip(texts, sources)]
        total = self.index.ntotal if _HAS_FAISS else len(self.meta)
        return len(texts), total

    def save(self, base_dir: str = VECTOR_DIR):
        d = Path(base_dir)
        d.mkdir(parents=True, exist_ok=True)
        if not _HAS_FAISS or self.index is None:
            return
        faiss.write_index(self.index, str(d / "store.index"))
        with open(d / "meta.json", "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False)

    def load(self, base_dir: str = VECTOR_DIR) -> bool:
        d = Path(base_dir)
        idx_path = d / "store.index"
        meta_path = d / "meta.json"
        if not meta_path.exists():
            return False
        if _HAS_FAISS:
            if not idx_path.exists():
                return False
            self.index = faiss.read_index(str(idx_path))
        else:
            return False
        with open(meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        if _HAS_FAISS and self.index.ntotal != len(self.meta):
            return False
        self.dim = self.index.d if _HAS_FAISS else None
        return True

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        if not _HAS_FAISS and not hasattr(self, "_fallback_matrix"):
            return []
        if _HAS_FAISS and self.index is None:
            return []
        qv = self.emb.embed_one(query).astype(np.float32)
        n = np.linalg.norm(qv)
        if n > 0:
            qv = qv / n
        if _HAS_FAISS:
            D, I = self.index.search(np.array([qv]), k)
        else:
            M = self._fallback_matrix
            sims = (M @ qv)  # inner product on normalized vectors
            idxs = np.argsort(-sims)[:k]
            D = np.array([sims[idxs]])
            I = np.array([idxs])
        res = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.meta):
                continue
            item = dict(self.meta[idx])
            item["score"] = float(score)
            res.append(item)
        return res
