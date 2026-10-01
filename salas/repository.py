"""Acesso a dados desta funcionalidade. Funções compartilhadas estão em database.py."""
from database import executar_insert, executar_select


def inserir_sala(nome, predio, numero_de_ar, ar1, ar2, ar3, ar4):
    return executar_insert(
        """
        INSERT INTO salas
        (nome, predio, numero_de_ar, ar1, ar2, ar3, ar4)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (nome, predio, numero_de_ar, ar1, ar2, ar3, ar4),
    )


def lista_salas():
    return executar_select(
        """
        SELECT id, nome, codigo, predio
        FROM salas
        ORDER BY codigo, nome
        """
    )
