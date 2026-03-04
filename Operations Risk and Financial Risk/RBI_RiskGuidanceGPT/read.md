# RBI RiskGuidanceGPT

RAG assistant focused on RBI operational and financial risk guidance, combining FAISS-based retrieval with a streamlined FastAPI backend and a modern, WhatsApp-like frontend. Answers stream live with clear source citations.

## Features
- FastAPI backend with endpoints for ingestion, asking, streaming, health and analytics
- PDF ingestion, chunking and FAISS vector store
- Structured bullet-point answers grounded in retrieved content
- Streaming responses (SSE) for chat-like typing animation
- Source citations with filename and page
- Chat history persistence, copy-to-clipboard and download reply as PDF
- Minimal admin analytics page (indexed stats, recent queries)

## Tech Stack
- Backend: FastAPI, Uvicorn, LangChain (FAISS, loaders, splitters), python-dotenv
- Embeddings: sentence-transformers/all-MiniLM-L6-v2 (with local fallback)
- Frontend: HTML/CSS/JS
- Vector store: FAISS via LangChain

## Quick Start
- Prereqs: Python 3.10+, PowerShell on Windows
- Install deps:
  - `python -m venv .venv`
  - `.\\.venv\\Scripts\\Activate.ps1`
  - `pip install -r backend/requirements.txt`
- Run server:
  - `python -m uvicorn backend.app:app --host 127.0.0.1 --port 8020 --log-level info`
- Open UI:
  - `http://127.0.0.1:8020/ui/`

## Ingest Data
- Place PDFs under [backend/data](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/data)
- Click “Rebuild Index” in the UI, or:
  - `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8020/ingest -ContentType 'application/json'`
- Verify:
  - `http://127.0.0.1:8020/status`

## Using The App
- Ask in the composer at the bottom; answers stream into assistant bubbles
- Sources appear under each answer as “filename.pdf (Page n)”
- Copy or Download PDF from bubble actions
- Admin analytics page:
  - `http://127.0.0.1:8020/ui/admin.html`

## Endpoints
- GET [/health](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L82-L85)
- GET [/status](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L161-L168)
- POST [/ingest](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L121-L138)
- POST [/ask](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L169-L192)
- GET [/ask-stream](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L194-L221)
- GET [/admin/stats](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L223-L225)
- GET [/admin/queries](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L227-L229)

## Configuration
- Env file: [.env](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/.env)
  - DATA_DIR, INDEX_DIR, BACKEND_HOST, BACKEND_PORT, HF_EMBEDDING_MODEL, LOG_LEVEL
- Loader: [rag_pipeline.py](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/rag_pipeline.py)
- Vector store: [vector_store.py](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/vector_store.py)

## Troubleshooting
- Health returns not reachable:
  - Ensure uvicorn process is running; re-run start command
- Zero chunks after ingest:
  - Verify PDFs exist in data folder; re-run ingest; check [/debug/pdfs](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py#L93-L109)
- SSE errors:
  - The app falls back to POST /ask automatically

## Key Files
- Backend app: [app.py](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/app.py)
- Pipeline: [rag_pipeline.py](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/rag_pipeline.py)
- Vector store: [vector_store.py](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/backend/vector_store.py)
- Frontend: [index.html](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/frontend/index.html), [style.css](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/frontend/css/style.css), [app.js](file:///E:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Operations%20Risk%20and%20Financial%20Risk/RBI_RiskGuidanceGPT/frontend/js/app.js)
