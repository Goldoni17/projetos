"""Carregamento e preparação dos documentos de políticas."""

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rh_assistant.config import PDF_PATHS


def load_documents() -> list[Document]:
    documents: list[Document] = []
    for path in PDF_PATHS:
        for document in PyPDFLoader(str(path)).load():
            document.metadata["document"] = path.name
            documents.append(document)
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)


def categorize_documents(chunks: list[Document]) -> list[Document]:
    for chunk in chunks:
        text = chunk.page_content.casefold()
        if "férias" in text or "ferias" in text:
            category = "ferias"
        elif "home office" in text or "remoto" in text:
            category = "home_office"
        elif "conduta" in text or "ética" in text or "etica" in text:
            category = "conduta"
        else:
            category = "geral"
        chunk.metadata["categoria"] = category
    return chunks
