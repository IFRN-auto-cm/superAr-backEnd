"""Acesso a dados da funcionalidade de monitoramento."""
from database import executar_select


def buscar_dispositivo_por_atuador(atuador):
    return executar_select(
        """
        SELECT
            ac.id AS ar_cadastrado_id,
            s.id AS sala_id
        FROM ar_cadastrados ac
        INNER JOIN salas s
            ON s.id = ac.sala
        WHERE ac.atuador = %s
        """,
        (atuador,),
    )
