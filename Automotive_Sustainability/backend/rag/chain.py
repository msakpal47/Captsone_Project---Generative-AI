from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma


def build_chain(store: Chroma, llm: Any, prompt_template: str, top_k: int):
    retriever = store.as_retriever(search_kwargs={"k": top_k})
    prompt = PromptTemplate.from_template(prompt_template)
    if llm is None:
        def run(inputs: Dict[str, str]) -> Dict[str, Any]:
            # LangChain retrievers now use .invoke for retrieval
            docs = retriever.invoke(inputs["query"])
            context = "\n\n".join([d.page_content for d in docs])
            return {"result": context, "source_documents": docs}
        return {"invoke": run}
    else:
        def run(inputs: Dict[str, str]) -> Dict[str, Any]:
            q = inputs["query"]
            docs = retriever.invoke(q)
            context = "\n\n".join([d.page_content for d in docs])
            msg = llm.invoke(prompt.format(context=context, question=q))
            text = getattr(msg, "content", str(msg))
            return {"result": text, "source_documents": docs}
        return {"invoke": run}
