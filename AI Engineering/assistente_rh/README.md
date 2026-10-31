# Assistente de políticas internas de RH

Aplicação Streamlit que consulta políticas internas em PDF usando busca
semântica, reranking e respostas com fontes.

## Estrutura

- `app.py`: interface e fluxo da aplicação.
- `rh_assistant/config.py`: caminhos, modelos e identificação das fontes.
- `rh_assistant/ingestion.py`: leitura, divisão e categorização dos PDFs.
- `rh_assistant/vectorstore.py`: criação e persistência do índice vetorial.
- `rh_assistant/qa.py`: recuperação, reranking e geração das respostas.

## Preparação

Coloque estes arquivos PDF na pasta do projeto:

- `politica_ferias.pdf`
- `politica_home_office.pdf`
- `codigo_conduta.pdf`

Crie um arquivo `.env` com a chave da API Groq:

```env
GROQ_API_KEY=sua_chave
```

Instale as dependências listadas em `requirements.txt` e inicie a aplicação
na pasta `projeto03`:

```bash
streamlit run app.py
```

O índice vetorial é salvo em `chroma_rh/` e reutilizado enquanto os PDFs não
mudarem. O primeiro uso pode levar mais tempo porque o modelo de embeddings
precisa ser carregado.
