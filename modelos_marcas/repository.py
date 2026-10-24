from database import (
    executar_delete,
    executar_insert,
    executar_insert_many,
    executar_select,
    get_db,
)


def deletar_modelo_marca(modelo_marca_id):
    return executar_delete(
        """
        DELETE FROM modelos_marcas
        WHERE id = %s
        """,
        (modelo_marca_id,),
    )


def inserir_modelo_marca(marca, modelo):
    return executar_insert(
        "INSERT INTO modelos_marcas (marca, modelo) VALUES (%s, %s)",
        (marca, modelo),
    )


def associar_modelo_comandos(associacoes):
    executar_insert_many(
        """
        INSERT INTO modelosMarcas_comando
        (modelo_marcas, comando, comando_valor)
        VALUES (%s, %s, %s)
        """,
        associacoes,
    )


def atualizar_modelo_marca_comandos(
    marca,
    modelo,
    modelo_marcas_id,
    comandos_para_remover,
    comandos_para_salvar,
):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("START TRANSACTION")
        cursor.execute(
            """
            UPDATE modelos_marcas
            SET marca = %s, modelo = %s
            WHERE id = %s
            """,
            (marca, modelo, modelo_marcas_id),
        )

        for comando_id in comandos_para_remover:
            cursor.execute(
                """
                DELETE FROM modelosMarcas_comando
                WHERE modelo_marcas = %s
                  AND comando = %s
                """,
                (modelo_marcas_id, comando_id),
            )

        for associacao in comandos_para_salvar:
            cursor.execute(
                """
                INSERT INTO modelosMarcas_comando
                    (modelo_marcas, comando, comando_valor)
                VALUES
                    (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    comando_valor = VALUES(comando_valor)
                """,
                associacao,
            )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def listar_modelos_marcas():
    return executar_select(
        """
        SELECT id, marca, modelo
        FROM modelos_marcas
        ORDER BY marca, modelo
        """
    )


def buscar_dados_edicao_modelo_marca(modelo_marca_id):
    marca_modelo = executar_select(
        """
        SELECT id, marca, modelo
        FROM modelos_marcas
        WHERE id = %s
        ORDER BY marca, modelo
        """,
        (modelo_marca_id,),
    )
    comandos = executar_select(
        """
        SELECT
            c.id AS comando_id,
            c.nome AS comando_nome,
            CASE
                WHEN mmc.id IS NULL THEN false
                ELSE true
            END AS cadastrado_no_modelo
        FROM comandos c
        LEFT JOIN modelosMarcas_comando mmc
            ON mmc.comando = c.id
           AND mmc.modelo_marcas = %s
        ORDER BY c.nome
        """,
        (modelo_marca_id,),
    )
    return marca_modelo, comandos


def listar_comandos_por_modelo_marca(modelo_marca_id):
    return executar_select(
        """
        SELECT
            mmc.id AS associacao_id,
            mm.id AS modelo_marca_id,
            mm.marca,
            mm.modelo,
            c.id AS comando_id,
            c.nome AS comando_nome,
            mmc.comando_valor
        FROM modelosMarcas_comando mmc
        INNER JOIN modelos_marcas mm
            ON mm.id = mmc.modelo_marcas
        INNER JOIN comandos c
            ON c.id = mmc.comando
        WHERE mm.id = %s
        ORDER BY c.nome
        """,
        (modelo_marca_id,),
    )
