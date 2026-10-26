
# API de Automação Inteligente

API REST desenvolvida com Python, FastAPI e OpenAI para analisar solicitações de automação e recomendar tecnologias de implementação.

## Tecnologias

- Python
- FastAPI
- OpenAI API
- Pydantic
- Structured Outputs

## Funcionalidades

- Classificação de solicitações de automação
- Recomendação de tecnologias: Requests, Playwright e IA
- Identificação de múltiplas tecnologias
- Classificação de complexidade
- Geração de justificativas técnicas
- Sinalização de necessidade de revisão humana
- Validação de entradas e respostas

## Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/automacao-inteligente-api.git
cd automacao-inteligente-api
```

Crie um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure a chave da OpenAI:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com sua chave.

## Executar

```bash
uvicorn api:app --reload --port 8000
```

Documentação interativa:

http://127.0.0.1:8000/docs

## Exemplo de utilização

POST /analisar

```json
{
  "texto": "Preciso utilizar uma API REST para baixar contratos e interpretar cláusulas utilizando IA."
}
```

Exemplo de resposta:

```json
{
  "categoria": "JURIDICO",
  "complexidade": "MEDIA",
  "tecnologias": [
    "REQUESTS",
    "IA"
  ],
  "justificativa": "A solicitação envolve integração HTTP e interpretação de contratos.",
  "revisao_humana": true
}
```

## Limitações

Este é um projeto de estudo e portfólio.

As recomendações geradas por IA podem conter erros e precisam de validação técnica.

A sinalização de revisão humana não implementa um fluxo de aprovação.

A aplicação ainda não possui autenticação nem mecanismos completos de proteção contra abuso.

## Próximas melhorias

- Testes automatizados
- Autenticação da API
- Monitoramento de custos e tokens
- Integração com ferramentas de RPA
- Implementação de agentes inteligentes

## Autor

Desenvolvedor Python com foco em RPA e Automação Inteligente.
