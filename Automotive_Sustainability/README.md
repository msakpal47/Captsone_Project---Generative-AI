Automotive Sustainability Chatbot

Overview
- FastAPI + LangChain RAG backend with Chroma persistence
- Sentence‑Transformers embeddings by default; optional OpenAI LLM/embeddings via .env
- Single‑page frontend with multi‑question submit and bottom fixed Ask bar

Quick Start
- Install: python -m pip install -r backend/requirements.txt
- Run server: python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8080
- Open UI: http://localhost:8080/ui
- Ingest: click Ingest (uses data/Automotive_Sustainability.pdf or project root fallback)
- Ask: type one or many questions (newline or “;” separated) and click Ask

Endpoints
- GET /healthz → status
- POST /ingest → body: JSON string path or null; builds Chroma index
- POST /ask → body: {"question": "...", "session_id": "web"}; returns {"answer","sources","history"}

Environment
- OPENAI_API_KEY=... (optional)
- USE_OPENAI_LLM=1 to enable OpenAI LLM
- USE_OPENAI_EMBEDDINGS=1 to use OpenAI embeddings
- EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2 (default)
- VECTORSTORE_DIR=vectorstore/chroma_index
- DATA_PDF=data/Automotive_Sustainability.pdf

Architecture
- Backend app: [app.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/app.py)
- PDF loader: [loader.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/rag/loader.py)
- Splitter: [splitter.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/rag/splitter.py)
- Embeddings: [embeddings.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/rag/embeddings.py) and [config.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/config.py)
- Vector store: [vector_store.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/rag/vector_store.py)
- RAG chain: [chain.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/rag/chain.py)
- Prompt: [prompt_template.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/utils/prompt_template.py)
- Session memory: [memory.py](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/backend/utils/memory.py)
- Frontend: [index.html](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/frontend/index.html), [style.css](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/frontend/css/style.css), [script.js](file:///e:/Data_Scientist_Project/Captsone_Project%20-%20Generative%20AI/Automotive_Sustainability/frontend/js/script.js)

Testing
- Run: python -m unittest discover -s tests -p "test_*.py" -q

Troubleshooting
- Use http://localhost:8080/ui instead of 0.0.0.0
- First ingest may download models; wait and retry
- If OpenAI is enabled, ensure OPENAI_API_KEY is set

Summary CSV
- See Project_summary.csv at the repo root for a one‑page component summary
