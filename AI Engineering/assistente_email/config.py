import os
from typing import Literal

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

PROFILE = {
    "name": "Sarah",
    "full_name": "Sarah Chen",
    "user_profile_background": "Engenheira de software sênior liderando uma equipe de 5 desenvolvedores",
}

PROMPT_INSTRUCTIONS = {
    "triage_rules": {
        "ignore": "Newsletters, spam, comunicados gerais da empresa",
        "notify": "Membro da equipe doente, notificações do sistema de build, atualizações de status de projeto",
        "respond": "Perguntas diretas de membros da equipe, solicitações de reunião, relatórios de bugs críticos",
    },
    "agent_instructions": """Você é um assistente executivo altamente eficiente. Execute as tarefas solicitadas de forma direta, sem diálogos desnecessários. Responda apenas com a chamada das ferramentas, a menos que seja estritamente necessário fornecer uma resposta textual.

Tarefas:
- Responder ao e-mail de entrada.
- Salvar a tarefa de acompanhamento na memória.
- Sugerir uma próxima ação, como 'Gostaria que eu agendasse uma reunião para discutir isso?'"""
}

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
    google_api_key=GOOGLE_API_KEY,
)

class Router(BaseModel):
    reasoning: str
    classification: Literal["ignore", "notify", "respond"]

llm_router = llm.with_structured_output(Router)

TRIAGE_SYSTEM_PROMPT = """Você é um assistente de triagem de e-mails.
Classifique os e-mails como 'ignore', 'notify' ou 'respond'.

Regras:
- ignore: {triage_no}
- notify: {triage_notify}
- respond: {triage_email}
"""

TRIAGE_USER_PROMPT = """
De: {author}
Para: {to}
Assunto: {subject}
Corpo da Mensagem:
{email_thread}
"""