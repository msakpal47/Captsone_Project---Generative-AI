from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from .config import DATA_DIR, VECTOR_DIR, APP_HOST, APP_PORT, TOP_K
from .vector_store import VectorStore
from .rag_pipeline import RAGPipeline
import uvicorn
import os
from pathlib import Path

app = FastAPI(title="TelecomRetainGPT API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = VectorStore()
store_loaded = store.load(VECTOR_DIR)
pipeline = RAGPipeline(store)


class IngestResponse(BaseModel):
    chunks: int
    vectors: int
    saved: bool

class IngestDebugResponse(BaseModel):
    candidates: list
    files_found: int
    chunks: int
    vectors: int
    saved: bool


class ChatRequest(BaseModel):
    message: str
    top_k: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list


@app.get("/health")
def health():
    return {"status": "ok", "index": store.index.ntotal if store.index else 0}


@app.post("/api/ingest", response_model=IngestResponse)
def ingest():
    try:
        chunks, vectors = store.build_from_pdfs(DATA_DIR)
        saved = False
        if vectors > 0:
            store.save(VECTOR_DIR)
            saved = True
        return IngestResponse(chunks=chunks, vectors=vectors, saved=saved)
    except Exception as e:
        return IngestResponse(chunks=0, vectors=0, saved=False)

@app.get("/api/ingest_debug")
def ingest_debug():
    from pathlib import Path as _Path
    base = _Path(__file__).resolve().parent.parent
    candidates = []
    p = _Path(DATA_DIR)
    if p.exists():
        candidates.append(str(p))
    candidates.append(str(base / "backend" / "data"))
    candidates.append(str(base))
    candidates.append(str(base.parent))
    try:
        files = []
        for c in candidates:
            cp = _Path(c)
            if not cp.exists():
                continue
            files.extend([str(x) for x in list(cp.glob("*.pdf")) + list(cp.glob("*.docx")) + list(cp.glob("*.txt"))])
        chunks, vectors = store.build_from_pdfs(DATA_DIR)
        saved = False
        if vectors > 0:
            store.save(VECTOR_DIR)
            saved = True
        return {"candidates": candidates, "files_found": len(files), "chunks": chunks, "vectors": vectors, "saved": saved}
    except Exception as e:
        return {"error": str(e), "candidates": candidates}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        k = req.top_k or TOP_K
        res = pipeline.answer(req.message, top_k=k)
        return ChatResponse(answer=res["answer"], sources=res["sources"])
    except Exception as e:
        return ChatResponse(answer=f"Server error: {str(e)}", sources=[])


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


@app.get("/")
def root():
    return RedirectResponse(url="/app")


if __name__ == "__main__":
    uvicorn.run("backend.app:app", host=APP_HOST, port=APP_PORT, reload=True)
