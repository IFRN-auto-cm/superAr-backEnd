from database import executar_select

def listar_modelos_marcas():
    try:
        resultado = executar_select(
            """
            SELECT id, marca, modelo
            FROM modelos_marcas
            ORDER BY marca, modelo
            """
        )

        return {"status": "ok", "dados": resultado}

    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}
