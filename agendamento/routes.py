from flask import Blueprint, jsonify

bp = Blueprint("agendamento", __name__)


@bp.route("/agendamentos", methods=["GET"])
def obter_agendamentos():
    dados = [
        {
            "id": 1,
            "nome": "Ligar sala de aula",
            "dias_semana": [
                True, True, True, True, True, False, False
            ],
            "horario": "07:00:00",
            "acoes": [
                {
                    "id": 1,
                    "comando_id": 1,
                    "comando_nome": "Ligar",
                    "valor": "23",
                    "ordem": 1,
                    "aparelho": {
                        "id": 3,
                        "nome": "Ar do laboratório"
                    }
                }
            ],
            "periodo_validade": {
                "inicio": "2026-10-01T00:00:00",
                "fim": None
            },
            "ativo": True
        }
    ]

    return jsonify({
        "status": "ok",
        "dados": dados
    }), 200