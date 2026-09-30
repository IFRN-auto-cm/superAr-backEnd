from database import executar_insert, executar_select, executar_update


def inserir_ar_cadastrado(
    temperatura_referencia,
    modelo_marca,
    status,
    atuador,
    nome,
    sala,
):
    return executar_insert(
        """
        INSERT INTO ar_cadastrados
        (temperatura_referencia, modelo_marca, status, atuador, nome, sala)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (temperatura_referencia, modelo_marca, status, atuador, nome, sala),
    )


def atualizar_ar_cadastrado(
    ar_cadastrado_id,
    temperatura_medida,
    temperatura_referencia,
    modelo_marca,
    status,
    atuador,
    nome,
    sala,
):
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


def buscar_comando_ar(ar_cadastrado_id, comando_nome):
    return executar_select(
        """
        SELECT
            ar.id AS ar_id,
            ar.nome AS ar_nome,
            ar.atuador,
            ar.modelo_marca,
            c.id AS comando_id,
            c.nome AS comando_nome,
            mmc.comando_valor
        FROM ar_cadastrados ar
        INNER JOIN modelosMarcas_comando mmc
            ON mmc.modelo_marcas = ar.modelo_marca
        INNER JOIN comandos c
            ON c.id = mmc.comando
        WHERE ar.id = %s
          AND c.nome = %s
        """,
        (ar_cadastrado_id, comando_nome),
    )


def buscar_ar_para_edicao(ar_cadastrado_id):
    return executar_select(
        """
        SELECT
            ar.id,
            ar.nome AS nome_ar,
            ar.temperatura_referencia,
            s.nome AS sala_nome,
            s.id as sala_id,
            mm.id as mm_id,
            mm.marca,
            mm.modelo,
            ar.atuador
        FROM ar_cadastrados ar
        LEFT JOIN salas s
            ON ar.sala = s.id
        LEFT JOIN modelos_marcas mm
            ON ar.modelo_marca = mm.id
        WHERE ar.id = %s
        """,
        str(ar_cadastrado_id),
    )


def listar_ar_cadastrados():
    return executar_select(
        """
        SELECT
            ar.id,
            ar.nome AS nome_ar,
            ar.temperatura_referencia,
            s.nome AS sala_nome,
            s.codigo as sala_cod,
            mm.marca,
            mm.modelo,
            ar.atuador
        FROM ar_cadastrados ar
        LEFT JOIN salas s
            ON ar.sala = s.id
        LEFT JOIN modelos_marcas mm
            ON ar.modelo_marca = mm.id
        ORDER BY s.nome, ar.nome
        """
    )
