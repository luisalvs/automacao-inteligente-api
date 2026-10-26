
import os
import logging
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI, OpenAIError, RateLimitError, APITimeoutError
from pydantic import BaseModel, Field


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Automação Inteligente",
    version="1.0.0"
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0,
    max_retries=1
)


class Solicitacao(BaseModel):

    texto: str = Field(
        min_length=10,
        max_length=3000
    )


class AnaliseAutomacao(BaseModel):

    categoria: Literal[
        "VEICULAR",
        "FINANCEIRO",
        "DOCUMENTOS",
        "JURIDICO",
        "OUTROS"
    ]

    complexidade: Literal[
        "BAIXA",
        "MEDIA",
        "ALTA",
        "INDEFINIDA"
    ]

    tecnologias: list[
        Literal[
            "REQUESTS",
            "PLAYWRIGHT",
            "IA",
            "INDEFINIDA"
        ]
    ]

    justificativa: str

    revisao_humana: bool


def classificar_automacao(solicitacao: str):

    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions="""
        Você é um especialista em RPA Python
        e arquitetura de automações inteligentes.

        Analise a solicitação recebida.

        CATEGORIAS:
        - VEICULAR: veículos, placas e multas.
        - FINANCEIRO: cobranças, boletos e pagamentos.
        - DOCUMENTOS: leitura e extração de documentos.
        - JURIDICO: contratos, processos e cláusulas.
        - OUTROS: nenhuma das anteriores.

        TECNOLOGIAS:
        - REQUESTS: quando houver API HTTP disponível.
        - PLAYWRIGHT: quando precisar interagir
          com um navegador.
        - IA: quando precisar interpretar conteúdo
          não estruturado.
        - INDEFINIDA: quando não houver dados
          suficientes para recomendar tecnologia.

        REGRAS:
        - Use apenas informações da solicitação.
        - Uma automação pode usar várias tecnologias.
        - Priorize JURIDICO para análise de contratos.
        - Não invente a existência de APIs ou sistemas.
        - Use INDEFINIDA para complexidade quando
          faltarem informações técnicas.
        - Justifique brevemente a classificação.

        REVISÃO HUMANA:
        - Retorne revisao_humana = true quando a solicitação
        envolver decisões jurídicas, financeiras ou
        operações com consequências importantes.

        - Retorne revisao_humana = true quando houver
        informações insuficientes para uma recomendação
        confiável.

        - Retorne revisao_humana = false para tarefas
        simples e de baixo risco.

        - A necessidade de revisão humana deve ser avaliada
        considerando o risco da operação.
        """,
        input=solicitacao,
        text_format=AnaliseAutomacao
    )

    if response.output_parsed is None:
        raise HTTPException(
            status_code=502,
            detail="A IA não retornou uma análise válida"
        )

    if response.usage:
        logger.info(
            "Tokens utilizados: %s",
            response.usage.total_tokens
        )

    return response.output_parsed


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analisar", response_model=AnaliseAutomacao)
def analisar(dados: Solicitacao):

    try:
        resultado = classificar_automacao(dados.texto)
        return resultado

    except HTTPException:
        raise

    except RateLimitError:
        raise HTTPException(
            status_code=503,
            detail="Limite da API de IA atingido"
        )

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Tempo de resposta da IA excedido"
        )

    except OpenAIError:
        logger.exception("Falha na integração com OpenAI")
        raise HTTPException(
            status_code=502,
            detail="Erro na integração com a IA"
        )
