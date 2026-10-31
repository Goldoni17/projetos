"""Criação e carregamento do índice vetorial persistente."""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from rh_assistant.config import EMBEDDING_MODEL, INDEX_DIRECTORY
from rh_assistant.ingestion import categorize_documents, load_documents, split_documents


def build_vectorstore(source_signature: str) -> Chroma:
    index_path = INDEX_DIRECTORY / source_signature
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    if (index_path / "chroma.sqlite3").is_file():
        vectorstore = Chroma(
            collection_name="rh_policies",
            embedding_function=embeddings,
            persist_directory=str(index_path),
        )
        if vectorstore.get().get("ids"):
            return vectorstore

    chunks: list[Document] = categorize_documents(
        split_documents(load_documents())
    )
    if not chunks:
        raise ValueError("Os PDFs de políticas não possuem conteúdo para indexar.")

    index_path.mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="rh_policies",
        persist_directory=str(index_path),
    )
