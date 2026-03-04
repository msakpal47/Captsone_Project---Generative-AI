import os
from typing import Dict, Any, List
from .config import OPENAI_API_KEY, LLM_MODEL, TOP_K, USE_OPENAI_CHAT
from .vector_store import VectorStore
from openai import OpenAI


class RAGPipeline:
    def __init__(self, store: VectorStore):
        self.store = store

    def answer(self, question: str, top_k: int = TOP_K) -> Dict[str, Any]:
        docs = self.store.search(question, k=top_k)
        if OPENAI_API_KEY and str(USE_OPENAI_CHAT) == "1":
            try:
                client = OpenAI(api_key=OPENAI_API_KEY or None)
                context = "\n\n".join([d["text"] for d in docs]) if docs else ""
                system = "You are TelecomRetainGPT, an assistant focused on Indian telecom customer retention."
                if context.strip():
                    user = f"Context:\n{context}\n\nQuestion:\n{question}"
                else:
                    user = f"Question:\n{question}"
                resp = client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    temperature=0.2,
                )
                ans = resp.choices[0].message.content
                return {"answer": ans, "sources": docs}
            except Exception:
                # Fall back to non-LLM answer if OpenAI is unavailable
                pass
        if not docs:
            return {"answer": "No relevant information found.", "sources": []}
        joined = docs[0]["text"]
        return {"answer": joined[:512], "sources": docs}
