from .rag_pipeline import RAGPipeline

def build_index():
    pipe = RAGPipeline()
    info = pipe.ingest()
    if isinstance(info, dict):
        chunks = info.get("indexed_chunks", 0)
        docs = info.get("documents_found", 0)
        return f"Index created successfully: {chunks} chunks from {docs} documents" if chunks > 0 else f"No documents found"
    return f"Index created successfully: {int(info)} chunks"
