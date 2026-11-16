import json

from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool


@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Envia um e-mail para o destinatário especificado com o assunto e conteúdo fornecidos."""
    return json.dumps({"to": to, "subject": subject, "content": content})


@tool
def schedule_meeting(
    attendees: list[str],
    subject: str,
    duration_minutes: int,
    preferred_day: str,
) -> str:
    """Agenda uma reunião com os participantes especificados."""
    return (
        f"Reunião '{subject}' de {duration_minutes} minutos agendada "
        f"para {preferred_day} com {len(attendees)} participantes"
    )


@tool
def check_calendar_availability(day: str) -> str:
    """Verifica os horários disponíveis para o dia fornecido."""
    return f"Horários disponíveis em {day}: 9:00, 14:00, 16:00"


google_embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
store = InMemoryStore(index={"embed": google_embeddings})

manage_memory_tool = create_manage_memory_tool(
    store=store,
    namespace=("email_assistant", "{langgraph_user_id}", "collection")
)
search_memory_tool = create_search_memory_tool(
    store=store,
    namespace=("email_assistant", "{langgraph_user_id}", "collection")
)
