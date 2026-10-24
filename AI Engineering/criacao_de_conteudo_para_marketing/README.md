# Assistente de Criação de Conteúdo para Marketing

> Projeto de Engenharia de IA para apoiar a produção de conteúdo digital da **Clínica Essencial Saúde**.

## Visão geral

Este projeto propõe um assistente de IA que transforma um tema informado pela equipe em conteúdo adaptado ao canal de divulgação. A pessoa usuária define parâmetros como público, tom e tamanho; a aplicação monta as instruções e solicita ao modelo uma versão inicial pronta para revisão.

O objetivo é reduzir o esforço repetitivo de criação, facilitar a consistência editorial e apoiar a presença digital da clínica em canais como blog, Instagram e e-mail. O conteúdo gerado deve ser revisado pela equipe antes de ser publicado, especialmente quando tratar de saúde.

## Problema

A produção de conteúdo costuma disputar tempo com outras demandas da equipe. Criar textos manualmente para diferentes canais, manter um tom consistente e ajustar prompts a cada solicitação pode tornar a publicação pouco frequente e consumir horas de trabalho.

## Solução proposta

Uma interface simples para informar o tema e personalizar a geração. O sistema combina os campos selecionados em um prompt estruturado e envia a solicitação a um modelo de linguagem. A resposta pode incluir o texto principal, uma chamada para ação e hashtags, conforme as opções escolhidas.

## Funcionalidades previstas

- Gerar conteúdo a partir de um tema ou tópico.
- Adaptar a saída para Blog, Instagram, LinkedIn ou e-mail.
- Selecionar o tom da mensagem: informativo, inspirador, urgente ou informal.
- Definir o comprimento: curto, médio ou longo.
- Direcionar a comunicação para um público-alvo, como jovens adultos, famílias ou idosos.
- Opcionalmente incluir chamada para ação, hashtags e palavras-chave.
- Produzir uma versão inicial para edição e aprovação humana.

## Parâmetros de entrada

| Campo | Exemplos |
| --- | --- |
| Plataforma | Blog, Instagram, LinkedIn, e-mail |
| Tom | Informativo, inspirador, urgente, informal |
| Comprimento | Curto, médio, longo |
| Tema | Alimentação, saúde mental, exames de rotina, cuidados |
| Público-alvo | Jovens adultos, famílias, idosos |
| Chamada para ação (opcional) | Agendar consulta, converse com um especialista |
| Hashtags (opcional) | Ativar ou desativar |
| Palavras-chave (opcional) | Termos que devem aparecer no texto |

## Fluxo da aplicação

1. A equipe preenche os campos de conteúdo.
2. A aplicação valida e organiza os parâmetros.
3. Um prompt dinâmico orienta o modelo sobre canal, público, tom, tamanho e itens opcionais.
4. O modelo gera uma sugestão de conteúdo.
5. A equipe revisa, edita e aprova o material antes de publicar.

## Tecnologias previstas

- **Python** para a lógica da aplicação.
- **Groq API** como provedor de modelo de linguagem no protótipo.
- **LangChain** para integração com o modelo e organização dos prompts.
- **Google Colab** para prototipagem e experimentação.
- **Streamlit** como opção para uma interface web independente.

O provedor de modelo e a interface poderão ser substituídos ou ampliados conforme os requisitos do projeto.

## Cuidados editoriais

- O conteúdo gerado é um rascunho e precisa de aprovação humana.
- Informações sobre sintomas, diagnóstico, tratamento, medicamentos ou prevenção devem ser verificadas por profissionais habilitados antes da publicação.
- Não inserir dados pessoais ou informações identificáveis de pacientes nos prompts.
- Revisar precisão, tom, linguagem inclusiva, palavras-chave e adequação às regras de comunicação da clínica.


