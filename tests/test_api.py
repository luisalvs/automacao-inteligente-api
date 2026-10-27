
import httpx
from fastapi.testclient import TestClient
from openai import APIConnectionError, APITimeoutError
import api


client = TestClient(api.app)


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analisar_sucesso(monkeypatch):

    def mock_classificar(solicitacao):

        return api.AnaliseAutomacao(
            categoria="JURIDICO",
            complexidade="MEDIA",
            tecnologias=["REQUESTS", "IA"],
            justificativa="API REST e interpretação de contratos.",
            revisao_humana=True
        )

    monkeypatch.setattr(
        api,
        "classificar_automacao",
        mock_classificar
    )

    response = client.post(
        "/analisar",
        json={
            "texto": "Preciso baixar contratos e interpretar cláusulas."
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["categoria"] == "JURIDICO" 
    assert dados["complexidade"] == "MEDIA"
    assert dados["tecnologias"] == ["REQUESTS", "IA"]
    assert dados["revisao_humana"] is True


def test_analisar_texto_curto(monkeypatch):

    def nao_deveria_chamar(solicitacao):
        raise AssertionError(
            "OpenAI não deveria ser chamada"
        )

    monkeypatch.setattr(
        api,
        "classificar_automacao",
        nao_deveria_chamar
    )

    response = client.post(
        "/analisar",
        json={"texto": "Teste"}
    )

    assert response.status_code == 422


def test_analisar_erro_conexao(monkeypatch):

    def mock_erro(solicitacao):

        request = httpx.Request(
            "POST",
            "https://api.openai.com/v1/responses"
        )

        raise APIConnectionError(request=request)

    monkeypatch.setattr(
        api,
        "classificar_automacao",
        mock_erro
    )

    response = client.post(
        "/analisar",
        json={
            "texto": "Preciso realizar uma consulta de veículos."
        }
    )

    assert response.status_code == 502
    assert "detail" in response.json()


def test_analisar_timeout(monkeypatch):

    def mock_timeout(solicitacao):

        request = httpx.Request(
            "POST",
            "https://api.openai.com/v1/responses"
        )

        raise APITimeoutError(request=request)

    monkeypatch.setattr(
        api,
        "classificar_automacao",
        mock_timeout
    )

    response = client.post(
        "/analisar",
        json={
            "texto": "Preciso consultar documentos em um portal."
        }
    )

    assert response.status_code == 504
    assert "detail" in response.json()
    

def test_analisar_sem_texto(monkeypatch):

    def nao_deveria_chamar(solicitacao):
        raise AssertionError(
            "A classificação não deveria ser executada"
        )

    monkeypatch.setattr(
        api,
        "classificar_automacao",
        nao_deveria_chamar
    )

    response = client.post(
        "/analisar",
        json={}
    )

    assert response.status_code == 422

    dados = response.json()

    assert dados["detail"][0]["type"] == "missing"