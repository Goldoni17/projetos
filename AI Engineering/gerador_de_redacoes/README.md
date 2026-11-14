# Gerador de Redações com Gemini e LangGraph

Aplicação web em português que planeja, pesquisa, escreve e revisa redações. A interface é feita com Gradio; o fluxo de trabalho é orquestrado pelo LangGraph e usa a API do Google Gemini para gerar o texto e a API Tavily para pesquisar referências.

## Funcionalidades

- Geração de redações a partir de um tema informado pelo usuário.
- Pesquisa na web para reunir informações relevantes.
- Revisão opcional do texto, configurável de zero a três iterações.
- Persistência do estado do fluxo em SQLite (`checkpoints.db`).

## Requisitos

- Python 3.10 ou superior.
- Uma chave de API do Google Gemini.
- Uma chave de API da Tavily.

## Instalação e execução

1. Clone o repositório e entre na pasta do projeto.
2. Crie e ative um ambiente virtual:

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na pasta do projeto e informe suas chaves:

   ```dotenv
   GOOGLE_API_KEY=sua_chave_do_google
   TAVILY_API_KEY=sua_chave_da_tavily
   ```

   O projeto também aceita `GEMINI_API_KEY` no lugar de `GOOGLE_API_KEY`.
   **Não publique o arquivo `.env` nem compartilhe suas chaves.**

5. Inicie a aplicação:

   ```bash
   python app.py
   ```

6. Abra no navegador o endereço exibido pelo Gradio (normalmente `http://127.0.0.1:7860`).

## Como usar

Digite o tema da redação, escolha o número máximo de revisões e selecione **Gerar Redação**. A geração requer conexão com a internet e utiliza as APIs do Google Gemini e Tavily, sujeitas às respectivas cotas e condições de uso.

## Estrutura do projeto

- `app.py`: interface Gradio e chamada do fluxo de geração.
- `backend.py`: grafo LangGraph, integração com Gemini/Tavily e persistência SQLite.
- `requirements.txt`: dependências Python.

O banco `checkpoints.db` é criado localmente e não precisa ser enviado ao GitHub.
