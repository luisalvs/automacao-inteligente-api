
import os
import logging
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import (
    OpenAI,
    OpenAIError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    APIStatusError
)


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


# Preços em USD por 1 milhão de tokens
# Modelo: gpt-4o-mini

PRECO_ENTRADA = 0.15
PRECO_ENTRADA_CACHE = 0.075
PRECO_SAIDA = 0.60


def calcular_custo(usage):

    entrada = usage.input_tokens
    saida = usage.output_tokens

    detalhes = usage.input_tokens_details

    cache = (
        detalhes.cached_tokens
        if detalhes is not None
        else 0
    )

    entrada_normal = max(0, entrada - cache)

    custo_entrada = (
        entrada_normal * PRECO_ENTRADA
    ) / 1_000_000

    custo_cache = (
        cache * PRECO_ENTRADA_CACHE
    ) / 1_000_000

    custo_saida = (
        saida * PRECO_SAIDA
    ) / 1_000_000

    return custo_entrada + custo_cache + custo_saida



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
        instructions= """
            Você é um especialista em automação de processos
            com Python, RPA e inteligência artificial.

            Analise a solicitação e retorne a classificação
            seguindo rigorosamente as regras abaixo.

            CATEGORIAS:
            - VEICULAR: consultas e automações relacionadas a veículos.
            - FINANCEIRO: dados financeiros, cobranças e pagamentos.
            - DOCUMENTOS: emissão, organização e processamento de documentos.
            - JURIDICO: contratos, legislação e processos jurídicos.
            - OUTROS: solicitações que não se enquadram nas anteriores.

            TECNOLOGIAS:
            - REQUESTS: quando a solicitação informar que existe
            uma API REST ou integração HTTP disponível.
            - PLAYWRIGHT: quando houver navegação em páginas,
            preenchimento de formulários ou interação com portais.
            - IA: quando for necessária interpretação,
            classificação ou extração semântica de informações.
            - INDEFINIDA: quando não houver informações suficientes
            para determinar a tecnologia.

            REGRAS OBRIGATÓRIAS:
            1. Nunca presuma a existência de uma API.
            2. Nunca presuma que será necessário usar navegador.
            3. Se a solicitação não informar o método de acesso
            aos dados, utilize INDEFINIDA para a tecnologia,
            salvo se outra tecnologia estiver claramente indicada.
            4. Quando duas ou mais tecnologias forem necessárias,
            retorne todas as tecnologias aplicáveis.
            5. Não invente informações ausentes.
            6. Quando a solicitação envolver interpretação jurídica,
            análise de risco ou decisões financeiras sensíveis,
            defina revisao_humana como true.
            7. Quando faltarem informações essenciais para uma
            decisão confiável, defina revisao_humana como true.
            8. Explique brevemente a justificativa da classificação.

            COMPLEXIDADE:
            - BAIXA: operação simples e bem definida.
            - MEDIA: múltiplas etapas ou integrações.
            - ALTA: fluxos complexos, múltiplos sistemas ou riscos elevados.
            - INDEFINIDA: informações insuficientes para avaliar.

            EXEMPLO:
            Solicitação: Preciso automatizar uma consulta de CPF.
            Categoria: OUTROS
            Tecnologias: INDEFINIDA
            Complexidade: INDEFINIDA
            Revisão humana: true

            Priorize a precisão e não faça suposições.
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

        entrada = response.usage.input_tokens
        saida = response.usage.output_tokens
        total = response.usage.total_tokens

        custo = calcular_custo(response.usage)

        if custo > 0.001:
            logger.warning(
                "ALERTA: custo elevado nesta requisição: US$ %.8f",
                custo
            )

        logger.info(
            "Modelo: %s | Entrada: %s | Saída: %s | "
            "Total: %s | Custo estimado: US$ %.8f",
            response.model,
            entrada,
            saida,
            total,
            custo
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

    except APITimeoutError:
        logger.warning("Timeout na comunicação com OpenAI")

        raise HTTPException(
            status_code=504,
            detail="Tempo limite de resposta da IA excedido"
        )

    except RateLimitError:
        logger.warning("Limite ou quota da OpenAI atingido")

        raise HTTPException(
            status_code=503,
            detail="Serviço de IA temporariamente indisponível"
        )

    except AuthenticationError:
        logger.error("Falha na autenticação da OpenAI")

        raise HTTPException(
            status_code=502,
            detail="Falha na configuração do provedor de IA"
        )

    except APIConnectionError:
        logger.warning("Falha de conexão com OpenAI")

        raise HTTPException(
            status_code=502,
            detail="Falha de comunicação com o serviço de IA"
        )

    except APIStatusError as erro:
        logger.error(
            "OpenAI retornou HTTP %s",
            erro.status_code
        )

        raise HTTPException(
            status_code=502,
            detail="O provedor de IA retornou um erro"
        )

    except OpenAIError:
        logger.exception("Erro inesperado no SDK da OpenAI")

        raise HTTPException(
            status_code=502,
            detail="Erro ao processar a solicitação com IA"
        )
