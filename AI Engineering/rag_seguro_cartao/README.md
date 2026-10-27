
# Assistente de benefícios de cartões

## ⚙️ Guia de Configuração

Configure o ambiente para executar o assistente RAG com Streamlit, Groq e
embeddings locais.

### 1. Criar e Ativar Ambiente Virtual

**Windows:**
```bash
python -m venv langchain
langchain\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv langchain
source langchain/bin/activate
```

### 2. Instalar Dependências

Utilize o comando abaixo para instalar as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 3. Configurar Chave da Groq

Crie ou edite o arquivo `.env` na pasta do projeto e adicione sua chave da Groq:
```bash
GROQ_API_KEY=sua_chave_groq
```

### 4. Iniciar a aplicação

Com o ambiente virtual ativado, instale as dependências e inicie a interface:
```bash
pip install -r requirements.txt
streamlit run app.py
```

Os guias PDF usados para responder às perguntas devem estar na pasta `documentos/`.
Na primeira inicialização, o modelo local de embeddings será baixado.
