"""Acesso a dados da funcionalidade de comandos."""
from database import executar_delete, executar_insert, executar_select


def inserir_comando(nome):
    return executar_insert(
        "INSERT INTO comandos (nome) VALUES (%s)",
        (nome,),
    )


def deletar_comando(comando_id):
    return executar_delete(
        """
        DELETE FROM comandos
        WHERE id = %s
        """,
        (comando_id,),
    )


def listar_comandos():
    return executar_select(
        """
        SELECT id, nome
        FROM comandos
        ORDER BY nome
        """
    )
