"""Acesso a dados desta funcionalidade. Funções compartilhadas estão em database.py."""
from database import (get_db, executar_select, executar_insert,
                      executar_insert_many, executar_update, executar_delete)



def executar_update(ar_cadastrado_id,
    temperatura_medida,
    temperatura_referencia,
    modelo_marca,
    status,
    atuador,
    nome,
    sala): 
    
    return executar_update(
            """
            UPDATE ar_cadastrados
            SET
                temperatura_medida = %s,
                temperatura_referencia = %s,
                modelo_marca = %s,
                status = %s,
                atuador = %s,
                nome = %s,
                sala = %s
            WHERE id = %s
            """,
            (
                temperatura_medida,
                temperatura_referencia,
                modelo_marca,
                status,
                atuador,
                nome,
                sala,
                ar_cadastrado_id,
            ),
        )
