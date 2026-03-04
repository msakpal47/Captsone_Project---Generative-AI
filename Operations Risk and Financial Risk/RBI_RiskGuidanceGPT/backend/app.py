from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .rag_pipeline import RAGPipeline
from . import config
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import os
import shutil
import logging
import json
from datetime import datetime

app = FastAPI(title="RBI RiskGuidanceGPT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RAGPipeline()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
analytics: Dict[str, Any] = {"queries": []}

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="ui")

class AskRequest(BaseModel):
    question: str
    k: Optional[int] = 4

class AskResponse(BaseModel):
    answer: str
    sources: List[Any]

@app.on_event("startup")
def on_startup():
    try:
        config.ensure_dirs()
        base_dir = config.BASE_DIR
        src_dir = base_dir.parent
        dst_dir = config.DATA_DIR
        try:
            faiss_dir = base_dir / "backend" / "faiss_index"
            backend_dir = base_dir / "backend"
            if faiss_dir.exists():
                for name in ["app.py", "vector_store.py", "rag_pipeline.py", "config.py", "requirements.txt", "cli_tools.py"]:
                    src_file = faiss_dir / name
                    if src_file.exists():
                        (backend_dir / name).write_bytes(src_file.read_bytes())
                        try:
                            src_file.unlink()
                        except Exception:
                            pass
        except Exception:
            pass
        candidates = [
            (src_dir / "operations risk.pdf", dst_dir / "operational_risk.pdf"),
            (src_dir / "financial risk.pdf", dst_dir / "financial_risk.pdf"),
        ]
        for src, dst in candidates:
            try:
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    src.replace(dst)
            except Exception:
                pass
    except Exception:
        pass
    try:
        pipeline.load_or_ingest()
    except Exception:
        pass

@app.get("/health")
def health():
    return {"ok": True, "status": "running"}

@app.get("/ui-index")
def ui_index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"error": "UI not found"}

@app.get("/debug/pdfs")
def debug_pdfs():
    items = []
    dirs = []
    if config.DATA_DIR.exists():
        dirs.append(config.DATA_DIR)
    if config.BASE_DIR.exists():
        dirs.append(config.BASE_DIR)
    seen = set()
    for d in dirs:
        for p in Path(d).rglob("*.pdf"):
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            items.append(rp)
    return {"count": len(items), "files": items}

@app.get("/")
def root():
    try:
        from .vector_store import index_exists
        ready = bool(pipeline.vs) or index_exists(config.INDEX_DIR)
    except Exception:
        ready = bool(pipeline.vs)
    status = "ready" if ready else "index_missing"
    return {"status": status, "data_dir": str(config.DATA_DIR), "index_dir": str(config.INDEX_DIR)}

@app.post("/ingest")
def ingest():
    try:
        logging.info("ingest_start")
        info = pipeline.ingest()
        if isinstance(info, dict):
            if info.get("indexed_chunks", 0) == 0 and info.get("documents_found", 0) == 0:
                info.setdefault("message", "No documents found in data locations")
            logging.info("ingest_done %s", json.dumps(info))
            return info
        # Fallback for legacy int return
        n = int(info)
        logging.info("ingest_done {\"indexed_chunks\": %s}", n)
        return {"indexed_chunks": n}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

def _rebuild_task():
    try:
        shutil.rmtree(config.INDEX_DIR, ignore_errors=True)
    except Exception:
        pass
    try:
        config.ensure_dirs()
    except Exception:
        pass
    pipeline.ingest()

@app.post("/api/rebuild-index")
def rebuild_index(background_tasks: BackgroundTasks):
    background_tasks.add_task(_rebuild_task)
    return {"started": True}

@app.get("/api/rebuild-index")
def rebuild_index_get(background_tasks: BackgroundTasks):
    background_tasks.add_task(_rebuild_task)
    return {"started": True}

@app.get("/status")
def status():
    try:
        from .vector_store import index_exists
        ready = bool(pipeline.vs) or index_exists(config.INDEX_DIR)
    except Exception:
        ready = bool(pipeline.vs)
    return {"ready": ready, "last_index": getattr(pipeline, "last_index_info", None)}
@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        if not pipeline.vs:
            raise HTTPException(status_code=400, detail="Index not ready. Ingest documents first.")
        logging.info("ask_query %s", req.question)
        result = pipeline.answer(req.question, k=req.k or 4)
        logging.info("ask_done %s", json.dumps({"sources": result.get("sources", [])})[:300])
        srcs = []
        for s in result.get("sources", []):
            try:
                srcs.append(f"{s.get('source','unknown')} (Page {s.get('page','')})")
            except Exception:
                srcs.append(str(s))
        try:
            analytics["queries"].append({"question": req.question, "ts": datetime.utcnow().isoformat(timespec="seconds")+"Z", "sources_count": len(srcs)})
            analytics["queries"] = analytics["queries"][-500:]
        except Exception:
            pass
        return AskResponse(answer=result["answer"], sources=srcs)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ask failed: {e}")

@app.get("/ask-stream")
def ask_stream(question: str, k: int = 4):
    try:
        if not pipeline.vs:
            raise HTTPException(status_code=400, detail="Index not ready. Ingest documents first.")
        logging.info("ask_stream_query %s", question)
        result = pipeline.answer(question, k=k or 4)
        txt = result.get("answer", "")
        srcs_list = []
        for s in result.get("sources", []):
            try:
                srcs_list.append(f"{s.get('source','unknown')} (Page {s.get('page','')})")
            except Exception:
                srcs_list.append(str(s))
        srcs = json.dumps(srcs_list)
        def _gen():
            yield "event: start\ndata: 1\n\n"
            step = 50
            for i in range(0, len(txt), step):
                chunk = txt[i:i+step]
                yield f"event: token\ndata: {chunk}\n\n"
            yield f"event: sources\ndata: {srcs}\n\n"
            yield "event: end\ndata: done\n\n"
        return StreamingResponse(_gen(), media_type="text/event-stream")
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ask stream failed: {e}")

@app.get("/admin/stats")
def admin_stats():
    return {"last_index": getattr(pipeline, "last_index_info", None)}

@app.get("/admin/queries")
def admin_queries():
    return analytics.get("queries", [])

if __name__ == "__main__":
    try:
        import uvicorn
        host = os.getenv("BACKEND_HOST", "0.0.0.0")
        port = int(os.getenv("BACKEND_PORT", "8000"))
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as ex:
        # fall back simple error
        print(f"Failed to start server: {ex}")
