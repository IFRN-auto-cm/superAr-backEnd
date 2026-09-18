from database import executar_select

def lista_salas():
    try:
        resultado = executar_select(
            """
            SELECT id, nome, codigo, predio
            FROM salas
            ORDER BY codigo, nome
            """
        )

        return {"status": "ok", "dados": resultado}

    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}
