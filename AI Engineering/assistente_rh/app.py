"""Interface Streamlit do assistente de políticas internas de RH."""

import streamlit as st
from dotenv import load_dotenv

from rh_assistant.config import PROJECT_DIRECTORY, get_api_key, get_source_signature
from rh_assistant.qa import answer_question
from rh_assistant.vectorstore import build_vectorstore

load_dotenv(PROJECT_DIRECTORY / ".env")

st.set_page_config(
    page_title="Políticas de RH",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def get_vectorstore(source_signature: str):
    return build_vectorstore(source_signature)


with st.sidebar:
    st.title("📚 Políticas de RH")
    st.caption("Assistente interno com respostas baseadas nos documentos da empresa.")
    st.divider()
    st.subheader("Assuntos disponíveis")
    st.markdown(
        "- Férias e ausências\n"
        "- Trabalho remoto\n"
        "- Código de conduta"
    )
    st.info(
        "As respostas são geradas a partir dos PDFs configurados. "
        "Confira as fontes antes de tomar decisões."
    )
    st.caption("Dica: inclua detalhes da situação na pergunta.")

st.title("Assistente de políticas internas")
st.markdown(
    "Consulte orientações de RH em linguagem natural. "
    "As respostas incluem os trechos usados como referência."
)

with st.form("question_form", clear_on_submit=False):
    question = st.text_area(
        "Como posso ajudar?",
        placeholder="Ex.: Como solicitar férias e com quanta antecedência?",
        height=110,
        max_chars=1200,
    )
    submitted = st.form_submit_button(
        "Consultar políticas",
        type="primary",
        use_container_width=True,
    )

if submitted:
    st.session_state.pop("last_result", None)
    normalized_question = question.strip()
    if not normalized_question:
        st.warning("Digite uma pergunta antes de consultar.")
    elif not get_api_key():
        st.error(
            "A variável GROQ_API_KEY não está configurada. "
            "Adicione-a ao arquivo .env do projeto."
        )
    else:
        try:
            signature = get_source_signature()
        except FileNotFoundError as error:
            st.error(str(error))
        else:
            with st.spinner("Pesquisando nos documentos e preparando a resposta..."):
                vectorstore = get_vectorstore(signature)
                response, sources = answer_question(normalized_question, vectorstore)
            st.session_state["last_result"] = {
                "question": normalized_question,
                "response": response,
                "sources": sources,
            }

result = st.session_state.get("last_result")
if result:
    st.divider()
    st.caption(f"Pergunta: {result['question']}")
    st.subheader("Resposta")
    st.markdown(result["response"])

    st.subheader("Fontes consultadas")
    if not result["sources"]:
        st.caption("Nenhum trecho relevante foi encontrado nos documentos.")
    else:
        for index, document in enumerate(result["sources"], start=1):
            source_name = document.metadata.get("document", "Documento sem nome")
            page_number = document.metadata.get("page")
            category = (
                document.metadata.get("categoria", "geral")
                .replace("_", " ")
                .title()
            )
            page_label = (
                f" · página {page_number + 1}"
                if isinstance(page_number, int)
                else ""
            )
            with st.expander(
                f"{index}. {source_name}{page_label} · {category}",
                expanded=index == 1,
            ):
                st.write(document.page_content)
