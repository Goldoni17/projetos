import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    api_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None

id_model = "openai/gpt-oss-120b"
llm = None
if api_key:
    llm = ChatGroq(
        model=id_model,
        groq_api_key=api_key,
        temperature=0.7,
        max_tokens=1024,
        timeout=60,
        max_retries=2,
    )


def llm_generate(llm, prompt):
    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Você é um especialista em marketing digital com foco em SEO e escrita persuasiva.",
            ),
            ("human", "{prompt}"),
        ]
    )

    chain = template | llm | StrOutputParser()
    return chain.invoke({"prompt": prompt})


st.set_page_config(page_title="Gerador de conteúdo 🤖", page_icon="🤖")
st.title("Gerador de Conteúdo")

topic = st.text_input(
    "Tema:",
    placeholder="Ex: saúde mental, alimentação saudável, prevensão, etc.",
)
platform = st.selectbox(
    "Plataforma:", ["Instagram", "Facebook", "LinkedIn", "Blog", "E-mail"]
)
tone = st.selectbox("Tom:", ["Normal", "Informativo", "Inspirador", "Urgente", "Informal"])
length = st.selectbox("Tamanho:", ["Curto", "Médio", "Longo"])
audience = st.selectbox(
    "Público Alvo",
    ["Geral", "Jovens Adultos", "Fámilias", "Idosos", "Adolescentes"],
)
cta = st.checkbox("Incluir CTA")
hashtags = st.checkbox("Retornar Hashtags")
keywords = st.text_area(
    "Palavras-chave (SEO): ",
    placeholder="Ex: Bem-estar, Medicina Preventiva...",
)

if st.button("Gerar conteúdo"):
    if not api_key:
        st.warning(
            "Chave da API da Groq não encontrada. Crie um arquivo .env com GROQ_API_KEY=..."
        )
        st.stop()

    if llm is None:
        llm = ChatGroq(
            model=id_model,
            groq_api_key=api_key,
            temperature=0.7,
            max_tokens=1024,
            timeout=60,
            max_retries=2,
        )

    prompt = f"""
    Escreva um texto com SEO otimizado sobre o tema '{topic}'.
    Retorne em sua resposta apenas o texto final e não inclua ela dentro de aspas.
    - Onde será publicado: {platform}.
    - Tom: {tone}.
    - Público Alvo: {audience}.
    - Comprimento: {length}.
    - {"Inclua uma chamada para ação clara." if cta else "Não inclua chamada para ação."}
    - {"Retorne ao final do texto hashtags relevantes." if hashtags else "Não inclua hashtags."}
    - {f"Palavras-chave para SEO: {keywords if keywords else 'Nenhuma'}"}
    """

    try:
        res = llm_generate(llm, prompt)
        st.markdown(res)
    except Exception as e:
        st.error(f"Erro ao gerar conteúdo: {e}")

    