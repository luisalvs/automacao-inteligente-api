from api import classificar_automacao


CASOS = [
    {
        "texto": (
            "Preciso consultar dados de veículos utilizando "
            "uma API REST disponível na empresa."
        ),
        "categoria": "VEICULAR",
        "tecnologias": ["REQUESTS"],
    },
    {
        "texto": (
            "Preciso abrir um portal web, preencher "
            "um formulário e clicar em Consultar."
        ),
        "categoria": "OUTROS",
        "tecnologias": ["PLAYWRIGHT"],
    },
    {
        "texto": (
            "Preciso interpretar contratos em PDF "
            "e identificar cláusulas importantes."
        ),
        "categoria": "JURIDICO",
        "tecnologias": ["IA"],
    },
    {
        "texto": "Preciso automatizar uma consulta de CPF.",
        "categoria": "OUTROS",
        "tecnologias": ["INDEFINIDA"],
    },
    {
        "texto": (
            "Preciso usar uma API REST para baixar contratos "
            "e interpretar cláusulas com inteligência artificial."
        ),
        "categoria": "JURIDICO",
        "tecnologias": ["REQUESTS", "IA"],
    },

    {   "texto": (
            "Preciso usar uma API REST para consultar informações de um boleto "
            "e enviar um email com o resultado."
        ),
        "categoria": "FINANCEIRO",
        "tecnologias": ["REQUESTS"],
    },
]


def avaliar():

    total = len(CASOS)
    acertos_categoria = 0
    acertos_tecnologia = 0
    acertos_completos = 0

    for numero, caso in enumerate(CASOS, start=1):

        try:

            resultado = classificar_automacao(caso["texto"])

            if resultado is None:
                print(f"[{numero}] Sem resposta estruturada")
                continue

            categoria_ok = (
                resultado.categoria == caso["categoria"]
            )

            tecnologia_ok = (
                set(resultado.tecnologias)
                == set(caso["tecnologias"])
            )

            acertos_categoria += int(categoria_ok)
            acertos_tecnologia += int(tecnologia_ok)
            acertos_completos += int(
                categoria_ok and tecnologia_ok
            )

            print(f"\nTESTE {numero}")
            print("Categoria:", resultado.categoria)
            print("Tecnologias:", resultado.tecnologias)

            print(
                "Categoria correta:",
                categoria_ok
            )

            print(
                "Tecnologias corretas:",
                tecnologia_ok
            )

        except Exception as erro:
            print(f"[{numero}] Erro: {type(erro).__name__}: {erro}")

    print("\n" + "=" * 45)
    print("RESULTADO DA AVALIAÇÃO")
    print("=" * 45)

    print(
        f"Categoria: {acertos_categoria}/{total} "
        f"({acertos_categoria / total:.0%})"
    )

    print(
        f"Tecnologias: {acertos_tecnologia}/{total} "
        f"({acertos_tecnologia / total:.0%})"
    )

    print(
        f"Acerto conjunto: {acertos_completos}/{total} "
        f"({acertos_completos / total:.0%})"
    )


if __name__ == "__main__":
    avaliar()
