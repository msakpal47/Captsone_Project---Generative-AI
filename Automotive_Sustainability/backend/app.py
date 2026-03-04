import os
import time
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from backend.config import (
    VECTORSTORE_DIR,
    DATA_PDF,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    EMBEDDINGS_MODEL,
    create_llm,
)
from backend.rag.loader import load_pdf
from backend.rag.splitter import split_documents
from backend.rag.embeddings import get_embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from backend.rag.vector_store import build_store, load_store
from backend.rag.chain import build_chain
from backend.utils.prompt_template import PROMPT_TEMPLATE
from backend.utils.memory import add_message, get_messages

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    app.mount("/ui", StaticFiles(directory=FRONTEND_DIR), name="ui")

@app.get("/ui", response_class=HTMLResponse)
@app.get("/ui/", response_class=HTMLResponse)
def ui_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h1>UI not found</h1>", status_code=404)

class AskRequest(BaseModel):
    question: str
    session_id: str = "default"


@app.get("/")
def root():
    return {"status": "ok", "message": "Automotive Sustainability RAG backend. Use /ingest and /ask."}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(path: str = Body(None)):
    t0 = time.perf_counter()
    target = path or DATA_PDF
    candidates = [
        target,
        os.path.abspath(target),
        os.path.join(os.path.dirname(__file__), "..", target),
        os.path.join(os.path.dirname(__file__), "..", "data", os.path.basename(target)),
        os.path.join(os.path.dirname(__file__), "..", os.path.basename(target)),
    ]
    chosen = None
    for p in candidates:
        if os.path.exists(p):
            chosen = os.path.abspath(p)
            break
    if chosen is None:
        return {"status": "error", "message": "PDF not found", "path": target}
    t1 = time.perf_counter()
    try:
        docs = load_pdf(chosen)
    except Exception as e:
        return {"status": "error", "message": f"Load error: {str(e)}"}
    t2 = time.perf_counter()
    try:
        chunks = split_documents(docs, CHUNK_SIZE, CHUNK_OVERLAP)
    except Exception as e:
        return {"status": "error", "message": f"Split error: {str(e)}"}
    t3 = time.perf_counter()
    try:
        embeddings = get_embeddings()
        store = build_store(chunks, embeddings, VECTORSTORE_DIR)
    except Exception as e:
        try:
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)
            store = build_store(chunks, embeddings, VECTORSTORE_DIR)
        except Exception as e2:
            return {"status": "error", "message": f"Embed/Persist error: {str(e2)}"}
    t4 = time.perf_counter()
    return {
        "status": "ok",
        "chunks": len(chunks),
        "persist_dir": VECTORSTORE_DIR,
        "timing": {
            "load_ms": int((t2 - t1) * 1000),
            "split_ms": int((t3 - t2) * 1000),
            "embed_persist_ms": int((t4 - t3) * 1000),
            "total_ms": int((t4 - t0) * 1000),
        },
    }


@app.post("/ask")
def ask(req: AskRequest):
    add_message(req.session_id, "user", req.question)
    embeddings = get_embeddings()
    store = load_store(embeddings, VECTORSTORE_DIR)
    llm = create_llm()
    chain = build_chain(store, llm, PROMPT_TEMPLATE, TOP_K)
    if hasattr(chain, "invoke"):
        result = chain.invoke({"query": req.question})
        answer = result["result"]
        sources = [{"source": d.metadata.get("source", ""), "page": d.metadata.get("page", 0)} for d in result["source_documents"]]
    else:
        result = chain["invoke"]({"query": req.question})
        answer = result["result"]
        sources = [{"source": d.metadata.get("source", ""), "page": d.metadata.get("page", 0)} for d in result["source_documents"]]
    add_message(req.session_id, "assistant", answer)
    return {"answer": answer, "sources": sources, "history": get_messages(req.session_id)}
