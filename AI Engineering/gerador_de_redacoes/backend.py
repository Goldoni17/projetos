import os
import sqlite3
from typing import TypedDict, List
from dotenv import load_dotenv
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int

class Queries(BaseModel):
    queries: List[str]

conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Chave passada explicitamente (verifique se o nome exato do modelo na sua conta é gemini-3.1-flash-lite ou gemini-3.1-flash-lite-preview)
model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

structured_model = model.with_structured_output(Queries)

def get_queries(prompt: str, task: str) -> Queries:
    result = structured_model.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=task)
    ])
    if isinstance(result, Queries):
        return result
    if isinstance(result, dict):
        return Queries.model_validate(result)
    raise TypeError(f"Esperava uma saída Queries, recebi {type(result).__name__}.")

PLAN_PROMPT = """Você é um escritor especialista com a tarefa de criar um esboço de alto nível para uma redação. \
Escreva esse esboço para o tópico fornecido pelo usuário. Apresente um plano da redação junto com quaisquer notas \
ou instruções relevantes para as seções."""

WRITER_PROMPT = """Você é um assistente de redação com a tarefa de escrever excelentes redações de 5 parágrafos. \
Gere a melhor redação possível para a solicitação do usuário e o esboço inicial. \
Se o usuário fornecer críticas, responda com uma versão revisada das suas tentativas anteriores. \
Utilize todas as informações abaixo conforme necessário:

------

{content}"""

REFLECTION_PROMPT = """Você é um professor avaliando uma redação enviada. \
Gere críticas e recomendações construtivas para o texto do usuário. \
Forneça recomendações detalhadas, incluindo sugestões sobre extensão, profundidade, estilo, clareza e estrutura."""

RESEARCH_PLAN_PROMPT = """Você é um pesquisador encarregado de fornecer informações que possam \
ser usadas na escrita da redação a seguir. Gere uma lista de consultas de pesquisa (search queries) em português \
que reúnam quaisquer informações relevantes. Gere no máximo 3 consultas."""

RESEARCH_CRITIQUE_PROMPT = """Você é um pesquisador encarregado de fornecer informações que possam \
ser usadas para fazer quaisquer revisões solicitadas (conforme descrito abaixo). \
Gere uma lista de consultas de pesquisa (search queries) em português que reúnam quaisquer informações relevantes. \
Gere no máximo 3 consultas."""

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def plan_node(state: AgentState):
    messages = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=state["task"])
    ]
    response = model.invoke(messages)
    return {"plan": response.content}

def research_plan_node(state: AgentState):
    queries = get_queries(RESEARCH_PLAN_PROMPT, state["task"])
    content = list(state.get("content") or [])
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response["results"]:
            content.append(r["content"])
    return {"content": content}

def generation_node(state: AgentState):
    content = "\n\n".join(state["content"] or [])
    user_message = HumanMessage(
        content=f'{state["task"]}\n\nHere is my plan:\n\n{state["plan"]}'
    )
    messages = [
        SystemMessage(
            content=WRITER_PROMPT.format(content=content)
        ),
        user_message
    ]
    response = model.invoke(messages)
    return {
        "draft": response.content,
        "revision_number": state.get("revision_number", 0) + 1
    }

def reflection_node(state: AgentState):
    messages = [
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state["draft"])
    ]
    response = model.invoke(messages)
    return {"critique": response.content}

def research_critique_node(state: AgentState):
    queries = get_queries(RESEARCH_CRITIQUE_PROMPT, state["critique"])
    content = list(state["content"] or [])
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response["results"]:
            content.append(r["content"])
    return {"content": content}

def should_continue(state):
    if state["revision_number"] > state["max_revisions"]:
        return END
    return "reflect"

builder = StateGraph(AgentState)
builder.add_node("planner", plan_node)
builder.add_node("research_plan", research_plan_node)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)
builder.add_node("research_critique", research_critique_node)

builder.set_entry_point("planner")

builder.add_conditional_edges(
    "generate",
    should_continue,
    {END: END, "reflect": "reflect"}
)

builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")
builder.add_edge("reflect", "research_critique")
builder.add_edge("research_critique", "generate")

graph = builder.compile(checkpointer=memory)

