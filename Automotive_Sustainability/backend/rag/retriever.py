from langchain_community.vectorstores import Chroma


def get_retriever(store: Chroma, top_k: int):
    return store.as_retriever(search_kwargs={"k": top_k})
