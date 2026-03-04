# TelecomRetainGPT

GenAI + RAG chatbot for Indian Telecom Customer Retention. It ingests PDFs/DOCX/TXT, builds a vector index, and answers questions with or without an OpenAI key. Designed to be reliable on Windows with fast, deterministic fallbacks.

## Features

- FastAPI backend exposing `/api/ingest`, `/api/chat`, `/health` and a simple web app at `/app`
- Ingestion of PDF/DOCX/TXT with robust extraction: PyPDF → pdfminer → optional OCR
- FAISS indexing with pure‑NumPy fallback (no FAISS required)
- Embeddings: OpenAI when enabled; deterministic hashing fallback otherwise
- Stable hot‑reload: vectors saved in `storage/vector_data` to avoid server restarts
- Frontend with “Build Index” and “Chat” pages

## Directory Layout

```
TelecomRetainGPT/
  backend/
    app.py            # FastAPI app (+ static frontend mount)
    config.py         # .env loader, defaults, chunking + flags
    embeddings.py     # OpenAI + hash embedding fallback
    rag_pipeline.py   # RAG answer flow + LLM fallback
    vector_store.py   # chunking, text extraction, FAISS / NumPy
    requirements.txt
  frontend/
    index.html, chat.html, css/, js/
  storage/
    vector_data/      # saved index and metadata
  .env
  run.bat / run.sh
```

## Quick Start

1. Python env and deps

```
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. Configure `.env` (already created with safe defaults)

```
OPENAI_API_KEY=            # optional
LLM_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=256
VECTOR_DIR=storage/vector_data
DATA_DIR=backend/data
TOP_K=4
APP_HOST=0.0.0.0
APP_PORT=8000
USE_OPENAI_EMBEDDINGS=0    # set 1 if you have a valid key
USE_OPENAI_CHAT=0          # set 1 if you have a valid key
CHUNK_SIZE=300
CHUNK_OVERLAP=50
```

3. Run the server

```
run.bat        # Windows
./run.sh       # Linux/macOS
```

4. Open the app

- Visit http://localhost:8000/app/
- Click “Build Index” (place PDFs/DOCX/TXT in `backend/data` or the project/parent folder)
- Expected for a text‑based PDF: `Chunks: 200+ • Vectors: 200+ • Saved: true`

## API

- `GET /health` → `{"status":"ok","index": <count>}`
- `POST /api/ingest` → `{"chunks": N, "vectors": N, "saved": true|false}`
- `POST /api/chat` body `{"message": "...", "top_k": 4}` → `{"answer": "...", "sources":[...]}`

## Configuration Flags

- `USE_OPENAI_EMBEDDINGS`: 1 enables OpenAI embeddings, 0 uses hashing fallback
- `USE_OPENAI_CHAT`: 1 uses OpenAI chat for final answers, 0 uses RAG only
- `CHUNK_SIZE`, `CHUNK_OVERLAP`: control chunk granularity and total vectors

## Troubleshooting

- `net::ERR_ABORTED http://localhost:8000/app/`
  - Cause: dev server restarted while writing index files, aborting in‑flight requests.
  - Fix: vectors are stored under `storage/vector_data` and server watches only `backend`.
  - Ensure you start via `run.bat` or `./run.sh`.

- Build Index returns `0, 0, false`
  - The file may be scanned (image‑only). Provide a text‑based PDF/DOCX/TXT or enable OCR.

- 401/Invalid API key in chat
  - Set `USE_OPENAI_CHAT=0` to use RAG without OpenAI, or supply a valid key and set to 1.

## Example Questions (30)

1. What are the top 5 prepaid retention strategies for Indian telcos?
2. Which segments show highest near‑term churn risk and why?
3. How should we prioritize offers for high‑ARPU prepaid users?
4. Which benefits reduce churn among price‑sensitive users?
5. What win‑back offers work for 30–90 day inactive customers?
6. Which channels perform best for each segment (SMS, WhatsApp, app, IVR)?
7. How do recharge frequency and tenure correlate with churn?
8. What signals predict likely migration to a competitor in 30 days?
9. Which cross‑sell bundles reduce churn for data‑heavy users?
10. How often should we refresh packs to prevent benefit fatigue?
11. What network KPIs most strongly correlate with churn?
12. How do app session patterns predict churn risk?
13. Which support issues commonly precede churn?
14. How do failed recharge attempts affect churn probability?
15. Are certain handset types linked to higher churn?
16. What KPIs should we track weekly for early churn signals?
17. How do we compute incremental retention vs. cost per saved user?
18. What A/B setup best measures retention lift?
19. Which attribution method suits multi‑channel campaigns?
20. How to set guardrails to avoid offer cannibalization?
21. How to tailor retention messaging by language and region?
22. Which combo packs minimize reliance on competitor add‑ons?
23. What is the optimal price ladder to reduce downgrade churn?
24. How to design proactive outreach for users with poor network KPIs?
25. What features most improve prepaid churn model accuracy?
26. How to set thresholds for high‑ vs medium‑risk users?
27. How to monitor and address churn model drift over time?
28. What uplift modeling approach picks the best users to target?
29. What governance steps ensure fair use of win‑back offers?
30. How to connect retention outcomes to revenue impact reliably?

## Notes on OCR

- To enable automatic OCR for scanned PDFs, install Tesseract and Poppler, then keep `pytesseract` and `pdf2image` installed (already in `requirements.txt`). The pipeline will attempt OCR when normal text extraction is empty.

## Security

- Do not commit API keys. `.env` is read at runtime; leave `OPENAI_API_KEY` blank unless local only.

## License

Proprietary/Project‑internal unless specified otherwise.

