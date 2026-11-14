import gradio as gr
from gradio.themes import Default
from backend import AgentState, graph
from langchain_core.runnables import RunnableConfig
import uuid

def generate_essay(topic: str, max_revisions: float) -> str:
    """
    Executa o grafo e retorna somente a redação final.
    """
    thread_id = str(uuid.uuid4())
    thread_config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    initial_state: AgentState = {
        "task": topic,
        "max_revisions": int(max_revisions),
        "revision_number": 0,
        "plan": "",
        "draft": "",
        "critique": "",
        "content": []
    }

    final_state = graph.invoke(initial_state, config=thread_config)
    return final_state["draft"]

# --- Criação da Interface Gradio ---
theme = Default(spacing_size="sm", text_size="sm")
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Gerador de Redações com Gemini e LangGraph")
    gr.Markdown(
        "Digite o tópico da sua redação e o número de revisões. "
        "O agente vai planejar, pesquisar, rascunhar e revisar o texto."
    )

    with gr.Row():
        essay_topic = gr.Textbox(label="Tópico da Redação", placeholder="Ex: A importância da inteligência artificial na educação")
        max_revisions_slider = gr.Slider(minimum=0, maximum=3, step=1, value=1, label="Número Máximo de Revisões")
        generate_button = gr.Button("Gerar Redação", variant="primary")

    output_textbox = gr.Textbox(label="Redação Final", lines=20, max_lines=40)

    # Associa o botão à função Python
    generate_button.click(
        fn=generate_essay,
        inputs=[essay_topic, max_revisions_slider],
        outputs=output_textbox
    )

# Lança a interface
if __name__ == "__main__":
    demo.launch(share=False, theme=theme)