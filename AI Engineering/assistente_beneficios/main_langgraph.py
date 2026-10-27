import os
import asyncio
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


load_dotenv()

modelo = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY"),
)

prompt_consultor_praia = ChatPromptTemplate.from_messages([
    ("system", "Apresente-se como Sra. Praia. Você é uma especialista em viagens com destinos para praia."),
    ("human", "{query}"),
])

prompt_consultor_montanha = ChatPromptTemplate.from_messages([
    ("system", "Apresente-se como Sr. Montanha. Você é um especialista em viagens com destinos para montanhas e atividades radicais."),
    ("human", "{query}"),
])

cadeia_praia = prompt_consultor_praia | modelo | StrOutputParser()
cadeia_montanha = prompt_consultor_montanha | modelo | StrOutputParser()


class Rota(BaseModel):
    destino: str = Field(description="praia ou montanha")


prompt_roteador = ChatPromptTemplate.from_messages([
    ("system", "Classifique a preferência de viagem do usuário entre praia ou montanha."),
    ("human", "{query}"),
])

roteador = prompt_roteador | modelo.with_structured_output(Rota, method="json_schema")


class Estado(TypedDict):
    query: str
    destino: Rota
    resposta: str


async def no_roteador(estado: Estado, config: RunnableConfig | None = None):
    destino = await roteador.ainvoke({"query": estado["query"]}, config)
    return {"destino": destino}


async def no_praia(estado: Estado, config: RunnableConfig | None = None):
    return {"resposta": await cadeia_praia.ainvoke({"query": estado["query"]}, config)}


async def no_montanha(estado: Estado, config: RunnableConfig | None = None):
    return {"resposta": await cadeia_montanha.ainvoke({"query": estado["query"]}, config)}


def escolher_no(estado: Estado) -> Literal["praia", "montanha"]:
    destino = estado["destino"].destino.lower() if isinstance(estado["destino"], Rota) else str(estado["destino"]).lower()
    return "praia" if destino == "praia" else "montanha"


grafo = StateGraph(Estado)

grafo.add_node("roteador", no_roteador)
grafo.add_node("praia", no_praia)
grafo.add_node("montanha", no_montanha)

grafo.add_edge(START, "roteador")
grafo.add_conditional_edges("roteador", escolher_no)
grafo.add_edge("praia", END)
grafo.add_edge("montanha", END)

app = grafo.compile()


async def main():
    resposta = await app.ainvoke(
        {"query": "Quero visitar um lugar no Brasil famoso por praias e cultura"}
    )
    print(resposta["resposta"])


if __name__ == "__main__":
    asyncio.run(main())