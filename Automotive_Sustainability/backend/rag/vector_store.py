from typing import List, Any
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


def build_store(docs: List[Document], embeddings: Any, persist_dir: str) -> Chroma:
    store = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_dir)
    store.persist()
    return store


def load_store(embeddings: Any, persist_dir: str) -> Chroma:
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)
