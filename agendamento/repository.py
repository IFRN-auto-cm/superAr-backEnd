from database import executar_select


def buscar_dados_agendamentos():
    agendamentos = executar_select("""
        SELECT
            id,
            nome,
            TIME_FORMAT(
                horario_acionamento,
                '%H:%i:%s'
            ) AS horario,
            inicio_validade,
            fim_validade,
            ativo
        FROM agendamentos
        ORDER BY id
    """)

    dias = executar_select("""
        SELECT
            agendamento_id,
            dia_semana
        FROM agendamentos_dias
        ORDER BY agendamento_id, dia_semana
    """)

    acoes = executar_select("""
        SELECT
            aa.id,
            aa.agendamento_id,
            aa.comando_id,
            c.nome AS comando_nome,
            aa.valor,
            aa.ordem,
            aa.ar_id AS aparelho_id,
            ar.nome AS aparelho_nome
        FROM agendamento_acoes AS aa
        LEFT JOIN comandos AS c
            ON c.id = aa.comando_id
        LEFT JOIN ar_cadastrados AS ar
            ON ar.id = aa.ar_id
        ORDER BY
            aa.agendamento_id,
            aa.ordem,
            aa.id
    """)

    return agendamentos, dias, acoes