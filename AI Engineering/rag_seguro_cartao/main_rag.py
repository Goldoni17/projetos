import os
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import SecretStr


ARQUIVOS_DOCUMENTOS = (
    "GTB_standard_Nov23.pdf",
    "GTB_gold_Nov23.pdf",
    "GTB_platinum_Nov23.pdf",
)


def criar_consultor() -> Callable[[str], tuple[str, list[Document]]]:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Configure a variável GROQ_API_KEY no arquivo .env.")

    pasta_documentos = Path(__file__).resolve().parent / "documentos"
    caminhos = [pasta_documentos / nome for nome in ARQUIVOS_DOCUMENTOS]
    arquivos_ausentes = [str(caminho) for caminho in caminhos if not caminho.is_file()]
    if arquivos_ausentes:
        raise FileNotFoundError(
            "Não foi possível encontrar os documentos necessários: "
            + ", ".join(arquivos_ausentes)
        )

    documentos = [
        documento
        for caminho in caminhos
        for documento in PyPDFLoader(str(caminho)).load()
    ]
    pedacos = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    ).split_documents(documentos)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    recuperador = FAISS.from_documents(pedacos, embeddings).as_retriever(
        search_kwargs={"k": 3}
    )
    modelo = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        api_key=SecretStr(api_key),
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Responda em português usando somente as informações do contexto. "
                "Se o contexto não trouxer a resposta, diga claramente que não "
                "encontrou essa informação nos documentos.",
            ),
            ("human", "Pergunta: {query}\n\nContexto:\n{contexto}"),
        ]
    )
    cadeia = prompt | modelo | StrOutputParser()

    def consultar(pergunta: str) -> tuple[str, list[Document]]:
        trechos = recuperador.invoke(pergunta)
        contexto = "\n\n".join(trecho.page_content for trecho in trechos)
        resposta = cadeia.invoke({"query": pergunta, "contexto": contexto})
        return resposta, trechos

    return consultar


if __name__ == "__main__":
    consultar = criar_consultor()
    resposta, _ = consultar(
        "Como devo proceder caso tenha um item comprado roubado e tenha o cartão Gold?"
    )
    print(resposta)
