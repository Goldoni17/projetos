from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate  
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.globals import set_debug 
from pydantic import Field, BaseModel

set_debug(True)

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# 1. Modelos Pydantic
class Destino(BaseModel):
    cidade: str = Field(description="A cidade recomendada para visitar")
    motivo: str = Field(description="Motivo pelo qual é interessante visitar essa cidade")

class Restaurantes(BaseModel):
    cidade: str = Field(description="A cidade recomendada para visitar")
    restaurantes: str = Field(description="Restaurantes recomendados na cidade")

parseador_destino = JsonOutputParser(pydantic_object=Destino)
parseador_restaurantes = JsonOutputParser(pydantic_object=Restaurantes)

# 2. Prompts
prompt_cidade = PromptTemplate(
    template="""
    Sugira apenas uma cidade dado o meu interesse por {interesse}.
    {formato_de_saida}
    """,
    input_variables=["interesse"],
    partial_variables={"formato_de_saida": parseador_destino.get_format_instructions()}
)

prompt_restaurantes = PromptTemplate(
    template="""
    Sugira restaurantes populares entre locais em {cidade}.
    {formato_de_saida}
    """,
    input_variables=["cidade"],
    partial_variables={"formato_de_saida": parseador_restaurantes.get_format_instructions()}
)

prompt_cultural = PromptTemplate(
    template="Sugira atividades e locais culturais em {cidade}.",
    input_variables=["cidade"]
)

modelo = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.5,
    api_key=api_key
)

# 3. Construção das sub-cadeias
cadeia1 = prompt_cidade | modelo | parseador_destino

# Usamos um dicionário/lambda para extrair a chave 'cidade' do JSON anterior 
# e repassar para o próximo prompt
cadeia2 = (
    {"cidade": lambda x: x["cidade"]} 
    | prompt_restaurantes 
    | modelo 
    | parseador_restaurantes
)

cadeia3 = (
    {"cidade": lambda x: x["cidade"]} 
    | prompt_cultural 
    | modelo 
    | StrOutputParser() # Instanciado corretamente com os parênteses ()
)

# 4. Cadeia principal unindo as etapas em sequência
# (A saída da cadeia1 vira entrada da cadeia2, e assim por diante)
cadeia_completa = cadeia1 | cadeia2 | cadeia3

resposta = cadeia_completa.invoke(
    {
        "interesse": "praias"
    }
) 
print(resposta)