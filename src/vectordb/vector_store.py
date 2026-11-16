from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import get_api_key, EMBED_MODEL


def build_vector_index(files: List[Tuple[str, str]]) -> FAISS:
    """files = [(file_name, extracted_text), ...] -> in-memory FAISS index."""
    api_key = get_api_key()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    documents = []
    for name, text in files:
        # metadatas makes every chunk remember which file it came from
        documents.extend(splitter.create_documents([text], metadatas=[{"source": name}]))

    if not documents:
        raise ValueError("No text could be extracted from the uploaded files.")

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=api_key)
    return FAISS.from_documents(documents, embeddings)