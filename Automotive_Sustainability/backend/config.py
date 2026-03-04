import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    OPENAI_API_KEY = OPENAI_API_KEY.strip().strip('"').strip("'")
OPENAI_EMBEDDINGS_MODEL = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
USE_OPENAI_LLM = os.getenv("USE_OPENAI_LLM", "0") == "1"
USE_OPENAI_EMBEDDINGS = os.getenv("USE_OPENAI_EMBEDDINGS", "0") == "1"
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTORSTORE_DIR = os.getenv(
    "VECTORSTORE_DIR", os.path.abspath(os.path.join("vectorstore", "chroma_index"))
)
DATA_PDF = os.getenv(
    "DATA_PDF", os.path.abspath(os.path.join("data", "Automotive_Sustainability.pdf"))
)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "4"))


def create_embeddings():
    if USE_OPENAI_EMBEDDINGS and OPENAI_API_KEY:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)


def create_llm():
    if USE_OPENAI_LLM and OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return None
