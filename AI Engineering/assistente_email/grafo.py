import json
from typing import Annotated, Literal, TypedDict

from langchain.agents import create_agent
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph, add_messages

from config import (
    PROFILE,
    PROMPT_INSTRUCTIONS,
    Router,
    TRIAGE_SYSTEM_PROMPT,
    TRIAGE_USER_PROMPT,
    llm,
    llm_router,
)
from tools import (
    check_calendar_availability,
    manage_memory_tool,
    search_memory_tool,
    schedule_meeting,
    store,
    write_email,
)


EmailInput = TypedDict(
    "EmailInput",
    {"from": str, "to": str, "subject": str, "body": str},
)


class EmailState(TypedDict, total=False):
    email_input: EmailInput
    messages: Annotated[list[AnyMessage], add_messages]
    next_step: Literal["respond", "end"]


AGENT_SYSTEM_PROMPT = """Você é o(a) assistente executivo(a) de {full_name}. Sua prioridade é maximizar o desempenho de {name}.
{instructions}

Ferramentas disponíveis:
- write_email(to, subject, content): prepara um e-mail para envio.
- schedule_meeting(attendees, subject, duration_minutes, preferred_day): agenda uma reunião.
- check_calendar_availability(day): consulta horários disponíveis.
- manage_memory e search_memory: salvam e consultam informações úteis.
"""

tools = [
    write_email,
    schedule_meeting,
    check_calendar_availability,
    manage_memory_tool,
    search_memory_tool,
]

response_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=AGENT_SYSTEM_PROMPT.format(
        full_name=PROFILE["full_name"],
        name=PROFILE["name"],
        instructions=PROMPT_INSTRUCTIONS["agent_instructions"],
    ),
    store=store,
)


def triage_router(state: EmailState) -> EmailState:
    email = state.get("email_input")
    if email is None:
        raise ValueError("O estado do grafo precisa conter email_input.")

    system_prompt = TRIAGE_SYSTEM_PROMPT.format(
        triage_no=PROMPT_INSTRUCTIONS["triage_rules"]["ignore"],
        triage_notify=PROMPT_INSTRUCTIONS["triage_rules"]["notify"],
        triage_email=PROMPT_INSTRUCTIONS["triage_rules"]["respond"],
    )
    user_prompt = TRIAGE_USER_PROMPT.format(
        author=email["from"],
        to=email["to"],
        subject=email["subject"],
        email_thread=email["body"],
    )
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    if not isinstance(result, Router):
        raise TypeError("O classificador não retornou um resultado Router válido.")

    if result.classification == "respond":
        message_content = json.dumps(email, ensure_ascii=False)
        return {
            "messages": [
                HumanMessage(content=f"Responda ao e-mail recebido: {message_content}")
            ],
            "next_step": "respond",
        }
    if result.classification in ("ignore", "notify"):
        return {"next_step": "end"}
    raise ValueError(f"Classificação inválida: {result.classification}")


builder = StateGraph(EmailState)
builder.add_node("triage_router", triage_router)
builder.add_node("response_agent", response_agent)
builder.set_entry_point("triage_router")
builder.add_conditional_edges(
    "triage_router",
    lambda state: state.get("next_step", "end"),
    {"respond": "response_agent", "end": END},
)
builder.add_edge("response_agent", END)
email_agent = builder.compile()


def human_in_the_loop_schedule(
    email_sender: str,
    email_recipient: str,
    email_subject: str,
    user_id: str = "lance",
) -> None:
    config: RunnableConfig = {"configurable": {"langgraph_user_id": user_id}}
    memories, _ = search_memory_tool.invoke(
        {"query": f"Reunião agendada para {email_sender}"},
        config=config,
    )

    if memories:
        email_content = write_email.invoke(
            {
                "to": email_sender,
                "subject": f"Re: {email_subject}",
                "content": "Olá, já agendei uma conversa para discutirmos esse assunto.",
            },
            config=config,
        )
        print(f"Resposta de confirmação: {email_content}")
        return

    decision = input(
        f"Deseja agendar uma reunião para discutir o pedido de {email_sender}? (sim/não): "
    ).strip().lower()

    if decision == "sim":
        meeting_output = schedule_meeting.invoke(
            {
                "attendees": [
                    email_recipient.split("<")[0].strip(),
                    email_sender.split("<")[0].strip(),
                ],
                "subject": f"Acompanhamento do pedido de {email_sender}",
                "duration_minutes": 30,
                "preferred_day": "amanhã",
            },
            config=config,
        )
        print(f"Resultado de schedule_meeting: {meeting_output}")

        memory_output = manage_memory_tool.invoke(
            {
                "action": "create",
                "content": f"Reunião agendada para discutir o pedido de {email_sender}",
            },
            config=config,
        )
        print(f"Resultado de manage_memory: {memory_output}")

        email_content = write_email.invoke(
            {
                "to": email_sender,
                "subject": f"Re: {email_subject}",
                "content": "Já agendei uma reunião para discutirmos esse assunto.",
            },
            config=config,
        )
        print(f"Resposta de confirmação: {email_content}")
        return

    email_content = write_email.invoke(
        {
            "to": email_sender,
            "subject": f"Re: {email_subject}",
            "content": "Estou acompanhando seu pedido e entrarei em contato assim que houver novidades.",
        },
        config=config,
    )
    print(f"Resposta de acompanhamento: {email_content}")

    memory_output = manage_memory_tool.invoke(
        {
            "action": "create",
            "content": f"E-mail de acompanhamento enviado para {email_sender}",
        },
        config=config,
    )
    print(f"Resultado de manage_memory: {memory_output}")