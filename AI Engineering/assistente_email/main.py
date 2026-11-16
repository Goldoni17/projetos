from config import GOOGLE_API_KEY
from grafo import EmailInput, EmailState, email_agent, human_in_the_loop_schedule
from langchain_core.runnables import RunnableConfig
from tools import manage_memory_tool


LANGGRAPH_USER_ID = "lance"

INITIAL_MEMORY_CONTENT = (
    "Acompanhamento necessário: Alice Smith perguntou sobre os endpoints de API "
    "ausentes na documentação do serviço de autenticação (/auth/refresh e "
    "/auth/validate). Sarah precisa revisar e esclarecer se eles foram "
    "intencionalmente omitidos ou se a documentação precisa de atualização."
)

SAMPLE_EMAIL: EmailInput = {
    "from": "Alice Smith <alice.smith@company.com>",
    "to": "Sarah Chen <sarah.chen@company.com>",
    "subject": "Acompanhamento",
    "body": "Olá Sarah, como está minha solicitação?",
}


def main() -> None:
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY no arquivo .env antes de executar o assistente."
        )

    config: RunnableConfig = {
        "configurable": {"langgraph_user_id": LANGGRAPH_USER_ID}
    }
    manage_memory_tool.invoke(
        {"action": "create", "content": INITIAL_MEMORY_CONTENT},
        config=config,
    )

    email_state: EmailState = {"email_input": SAMPLE_EMAIL}
    response = email_agent.invoke(email_state, config=config)
    for message in response.get("messages", []):
        if getattr(message, "type", None) == "tool":
            print(f"Ferramenta: {message.name}\nResultado: {message.content}")

    human_in_the_loop_schedule(
        SAMPLE_EMAIL["from"],
        SAMPLE_EMAIL["to"],
        SAMPLE_EMAIL["subject"],
        user_id=LANGGRAPH_USER_ID,
    )


if __name__ == "__main__":
    main()
