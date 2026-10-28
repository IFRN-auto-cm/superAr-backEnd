from datetime import datetime


def buscar_dados_simulados():
    agendamentos = [
        {
            "id": 1,
            "nome": "Ligar laboratório",
            "horario": "07:00:00",
            "inicio_validade": datetime(2026, 10, 1),
            "fim_validade": None,
            "ativo": True
        }
    ]

    dias = [
        {"agendamento_id": 1, "dia_semana": dia}
        for dia in range(5)
    ]

    acoes = [
        {
            "id": 1,
            "agendamento_id": 1,
            "comando_id": 1,
            "comando_nome": "Ligar",
            "valor": "23",
            "ordem": 1,
            "aparelho_id": 3,
            "aparelho_nome": "Ar do laboratório"
        },
        {
            "id": 2,
            "agendamento_id": 1,
            "comando_id": 2,
            "comando_nome": "Ligar",
            "valor": "23",
            "ordem": 2,
            "aparelho_id": 4,
            "aparelho_nome": "Ar do laboratório 2"
        }
    ]

    return agendamentos, dias, acoes    

def listar_agendamentos():
    registros, dias, acoes = buscar_dados_simulados()

    por_id = {}

    for registro in registros:
        agendamento_id = registro["id"]
        fim = registro["fim_validade"]

        por_id[agendamento_id] = {
            "id": agendamento_id,
            "nome": registro["nome"],
            "dias_semana": [False] * 7,
            "horario": registro["horario"],
            "acoes": [],
            "periodo_validade": {
                "inicio": registro["inicio_validade"].isoformat(),
                "fim": fim.isoformat() if fim is not None else None
            },
            "ativo": bool(registro["ativo"])
        }

    for registro in dias:
        agendamento = por_id[registro["agendamento_id"]]
        dia = registro["dia_semana"]

        if not 0 <= dia <= 6:
            raise ValueError("Dia da semana fora do intervalo 0 a 6")

        agendamento["dias_semana"][dia] = True

    for registro in acoes:
        agendamento = por_id[registro["agendamento_id"]]

        agendamento["acoes"].append({
            "id": registro["id"],
            "comando_id": registro["comando_id"],
            "comando_nome": registro["comando_nome"],
            "valor": registro["valor"],
            "ordem": registro["ordem"],
            "aparelho": {
                "id": registro["aparelho_id"],
                "nome": registro["aparelho_nome"]
            }
        })

    return list(por_id.values())