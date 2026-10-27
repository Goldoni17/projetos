import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from main_rag import ARQUIVOS_DOCUMENTOS, criar_consultor

load_dotenv()

st.set_page_config(
    page_title="Concierge de Benefícios",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {
        --bg-canvas: #F8FAFC;
        --bg-surface: #FFFFFF;
        --bg-sidebar: #0F172A;
        --bg-sidebar-card: #1E293B;
        --ink-primary: #0F172A;
        --ink-secondary: #475569;
        --ink-muted: #94A3B8;
        --accent-primary: #2563EB;
        --accent-hover: #1D4ED8;
        --accent-soft: #EFF6FF;
        --border-light: #E2E8F0;
        --border-sidebar: #334155;
        --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
        --shadow-md: 0 10px 25px -5px rgba(15, 23, 42, 0.05), 0 8px 10px -6px rgba(15, 23, 42, 0.02);
    }

    /* Base & Tipografia */
    .stApp {
        background-color: var(--bg-canvas);
        color: var(--ink-primary);
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #EFF6FF 0%, #F8FAFC 45%);
    }

    .block-container {
        max-width: 920px;
        padding-top: 2.8rem;
        padding-bottom: 8rem;
    }

    /* ==========================================================================
       CORREÇÃO 1: Botão de abrir/fechar a Barra Lateral sempre visível
       ========================================================================== */
    /* Botão de reabrir quando a sidebar está fechada (fundo claro na página) */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08) !important;
        color: #0F172A !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stExpandSidebarButton"] svg,
    header[data-testid="stHeader"] button svg {
        fill: #0F172A !important;
        color: #0F172A !important;
    }

    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="stExpandSidebarButton"]:hover {
        background-color: #EFF6FF !important;
        border-color: #2563EB !important;
    }

    /* Botão de recolher quando a sidebar está aberta (fundo escuro na sidebar) */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="stSidebar"] button[kind="headerNoPadding"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid var(--border-sidebar) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebar"] button[kind="header"] svg,
    [data-testid="stSidebar"] button[kind="headerNoPadding"] svg {
        fill: #F8FAFC !important;
        color: #F8FAFC !important;
    }

    /* Sidebar Escura Profissional */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar);
        border-right: 1px solid var(--border-sidebar);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.75rem 1.25rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #F8FAFC !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--border-sidebar);
        margin: 1.4rem 0;
    }

    /* Marca na Sidebar */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        padding-bottom: 1.5rem;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid var(--border-sidebar);
    }

    .brand-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #FFFFFF;
        font-size: 1.15rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }

    .brand-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .brand-subtitle {
        font-size: 0.75rem;
        color: #94A3B8;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Lista de Cartões na Sidebar */
    .section-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94A3B8 !important;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }

    .tier-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.5rem;
        background: var(--bg-sidebar-card);
        border: 1px solid var(--border-sidebar);
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #E2E8F0;
    }

    .tier-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }

    .tier-badge {
        font-size: 0.68rem;
        padding: 2px 8px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.07);
        color: #CBD5E1;
        font-weight: 600;
    }

    .sidebar-disclaimer {
        padding: 0.9rem 1rem;
        border-radius: 10px;
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid var(--border-sidebar);
        color: #94A3B8;
        font-size: 0.76rem;
        line-height: 1.55;
        margin-bottom: 1rem;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        width: 100%;
        box-sizing: border-box;
    }

    .status-online {
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .status-offline {
        background: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }

    /* Hero / Tela de Boas-Vindas */
    .hero-wrapper {
        text-align: center;
        padding: 1.5rem 0 2rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        background: var(--accent-soft);
        border: 1px solid #BFDBFE;
        color: var(--accent-primary);
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
    }

    .hero-title {
        font-size: clamp(2rem, 4vw, 2.75rem);
        font-weight: 700;
        color: var(--ink-primary);
        letter-spacing: -0.04em;
        line-height: 1.15;
        margin: 0 0 0.85rem;
    }

    .hero-title span {
        background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        max-width: 580px;
        margin: 0 auto;
        color: var(--ink-secondary);
        font-size: 1.02rem;
        line-height: 1.6;
        font-weight: 400;
    }

    .shortcut-header {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--ink-muted);
        margin: 0.5rem 0 0.85rem;
    }

    /* Botões de Atalho como Cards Interativos */
    div.stButton > button {
        border: 1px solid var(--border-light);
        border-radius: 14px;
        background: var(--bg-surface);
        color: var(--ink-primary);
        padding: 1rem 1.1rem;
        min-height: 5.5rem;
        text-align: left;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    div.stButton > button p {
        font-size: 0.88rem;
        line-height: 1.45;
        color: var(--ink-secondary);
    }

    div.stButton > button p strong {
        display: block;
        font-size: 0.95rem;
        color: var(--ink-primary);
        margin-bottom: 0.2rem;
    }

    div.stButton > button:hover {
        border-color: #93C5FD;
        background: #FFFFFF;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    div.stButton > button:hover p strong {
        color: var(--accent-primary);
    }

    /* Botão na Sidebar (Nova Conversa) */
    [data-testid="stSidebar"] div.stButton > button {
        min-height: 2.6rem;
        padding: 0.5rem 0.9rem;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid var(--border-sidebar);
        color: #F8FAFC;
        text-align: center;
        border-radius: 10px;
    }

    [data-testid="stSidebar"] div.stButton > button p {
        color: #F8FAFC !important;
        font-weight: 600;
        font-size: 0.82rem;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.12);
        border-color: #64748B;
        transform: none;
    }

    /* Mensagens do Chat */
    [data-testid="stChatMessage"] {
        border: 1px solid var(--border-light);
        border-radius: 16px;
        background: var(--bg-surface);
        padding: 1.15rem 1.35rem;
        margin-bottom: 0.9rem;
        box-shadow: var(--shadow-sm);
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: var(--ink-primary) !important;
        line-height: 1.65;
        font-size: 0.96rem;
    }

    /* Cartões de Fonte (Trechos Consultados) */
    .source-card {
        background: #F8FAFC;
        border: 1px solid var(--border-light);
        border-left: 3px solid var(--accent-primary);
        border-radius: 8px;
        padding: 0.75rem 0.95rem;
        margin-bottom: 0.65rem;
    }

    .source-header {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--ink-primary);
        margin-bottom: 0.35rem;
    }

    .source-excerpt {
        font-size: 0.82rem;
        color: var(--ink-secondary);
        line-height: 1.5;
        margin: 0;
    }

    /* ==========================================================================
       CORREÇÃO 2: Barra de Digitação com texto escuro nítido e fundo limpo
       ========================================================================== */
    [data-testid="stChatInput"] {
        border: 1px solid #CBD5E1 !important;
        border-radius: 14px !important;
        background-color: #FFFFFF !important;
        box-shadow: var(--shadow-md) !important;
        padding: 0.2rem 0.45rem !important;
    }

    /* Remove qualquer fundo escuro herdado do tema do navegador/Streamlit */
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] [data-baseweb="textarea"],
    [data-testid="stChatInput"] [data-baseweb="base-input"] {
        background-color: transparent !important;
        border: none !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }

    /* Cor do texto digitado e do cursor */
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInputTextArea"] {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        caret-color: #2563EB !important;
        background-color: transparent !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder,
    [data-testid="stChatInputTextArea"]::placeholder {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
        font-weight: 400 !important;
    }

    /* Botão de enviar mensagem dentro da barra */
    [data-testid="stChatInputSubmitButton"] {
        color: var(--accent-primary) !important;
    }

    [data-testid="stChatInputSubmitButton"] svg {
        fill: var(--accent-primary) !important;
    }

    [data-testid="stBottom"] {
        background: linear-gradient(180deg, rgba(248, 250, 252, 0) 0%, #F8FAFC 35%);
    }

    [data-testid="stBottom"] > div {
        background: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Indexando base de regulamentos e apólices...")
def obter_consultor():
    return criar_consultor()


if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

cores_categoria = {
    "Standard": "#38BDF8",
    "Gold": "#FBBF24",
    "Platinum": "#A78BFA",
}

with st.sidebar:
    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-icon">✦</div>
            <div>
                <div class="brand-title">Portal de Benefícios</div>
                <div class="brand-subtitle">Assistente Inteligente RAG</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Guias Indexados</div>', unsafe_allow_html=True)

    for arquivo in ARQUIVOS_DOCUMENTOS:
        partes = Path(arquivo).stem.split("_")
        nome_documento = partes[1].title() if len(partes) > 1 else Path(arquivo).stem.title()
        cor_ponto = cores_categoria.get(nome_documento, "#60A5FA")
        st.markdown(
            f"""
            <div class="tier-card">
                <div>
                    <span class="tier-dot" style="background-color: {cor_ponto};"></span>
                    Cartão {nome_documento}
                </div>
                <span class="tier-badge">Ativo</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.mensagens:
        st.write("")
        if st.button("↺ Iniciar nova consulta", use_container_width=True):
            st.session_state.mensagens = []
            st.rerun()

    st.divider()

    st.markdown(
        '<div class="sidebar-disclaimer">'
        "As orientações são extraídas diretamente dos regulamentos oficiais. "
        "Verifique os termos vigentes da sua apólice antes de acionar um sinistro."
        "</div>",
        unsafe_allow_html=True,
    )

    chave_configurada = bool(os.getenv("GROQ_API_KEY"))
    if chave_configurada:
        st.markdown(
            '<div class="status-pill status-online">● Motor de IA conectado</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-pill status-offline">○ Configure GROQ_API_KEY no .env</div>',
            unsafe_allow_html=True,
        )

atalhos = [
    {
        "titulo": "🛡️ Proteção de compras",
        "descricao": "Prazos, valores máximos e condições para itens adquiridos.",
        "pergunta": "Quais proteções existem para compras?",
    },
    {
        "titulo": "✈️ Assistência de viagem",
        "descricao": "Coberturas médicas, atrasos e serviços de emergência.",
        "pergunta": "Como funciona a assistência de viagem?",
    },
    {
        "titulo": "🔒 Roubo ou dano acidental",
        "descricao": "Como abrir sinistro e quais documentos apresentar.",
        "pergunta": "O que fazer em caso de roubo de um item?",
    },
]

if not any(mensagem["role"] == "user" for mensagem in st.session_state.mensagens):
    st.markdown(
        """
        <div class="hero-wrapper">
            <div class="hero-badge">✦ Central de Apólices & Coberturas</div>
            <h1 class="hero-title">Seus benefícios, <span>sem letras miúdas.</span></h1>
            <p class="hero-subtitle">
                Consulte coberturas, franquias e procedimentos de acionamento das categorias
                <strong>Standard</strong>, <strong>Gold</strong> e <strong>Platinum</strong> em segundos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="shortcut-header">Consultas frequentes</div>', unsafe_allow_html=True)
    colunas = st.columns(len(atalhos), gap="medium")
    for indice, item in enumerate(atalhos):
        label_cartao = f"**{item['titulo']}**\n\n{item['descricao']}"
        if colunas[indice].button(
            label_cartao,
            key=f"atalho_{indice}",
            use_container_width=True,
        ):
            st.session_state.pergunta_pendente = item["pergunta"]
            st.rerun()

pergunta_digitada = st.chat_input("Pergunte sobre coberturas, sinistros ou elegibilidade...")
pergunta = pergunta_digitada or st.session_state.pop("pergunta_pendente", None)

if pergunta:
    st.session_state.mensagens.append(
        {"role": "user", "content": pergunta, "sources": []}
    )
    if not os.getenv("GROQ_API_KEY"):
        st.session_state.mensagens.append(
            {
                "role": "assistant",
                "content": (
                    "Ainda não consigo consultar os documentos. Configure "
                    "`GROQ_API_KEY` no arquivo `.env` e reinicie o aplicativo."
                ),
                "sources": [],
            }
        )
    else:
        with st.spinner("Analisando regulamentos oficiais..."):
            consultar = obter_consultor()
            resposta, fontes = consultar(pergunta)
        st.session_state.mensagens.append(
            {"role": "assistant", "content": resposta, "sources": fontes}
        )
    st.rerun()

for mensagem in st.session_state.mensagens:
    avatar = "🧑‍💼" if mensagem["role"] == "user" else "✦"
    with st.chat_message(mensagem["role"], avatar=avatar):
        st.markdown(mensagem["content"])
        if mensagem["sources"]:
            with st.expander(f"📄 Ver trechos consultados ({len(mensagem['sources'])} referências)"):
                for fonte in mensagem["sources"]:
                    nome = Path(fonte.metadata.get("source", "Documento")).name
                    pagina = fonte.metadata.get("page")
                    referencia = f"{nome} • Pág. {pagina + 1}" if pagina is not None else nome
                    st.markdown(
                        f"""
                        <div class="source-card">
                            <div class="source-header">📌 {referencia}</div>
                            <p class="source-excerpt">{fonte.page_content}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )