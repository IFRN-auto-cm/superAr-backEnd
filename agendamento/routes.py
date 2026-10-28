from flask import Blueprint, current_app, jsonify

from .service import listar_agendamentos

bp = Blueprint("agendamento", __name__)


@bp.route("/agendamentos", methods=["GET"])
def obter_agendamentos():
    try:
        dados = listar_agendamentos()

        return jsonify({
            "status": "ok",
            "dados": dados
        }), 200

    except Exception:
        current_app.logger.exception(
            "Erro ao listar agendamentos"
        )

        return jsonify({
            "status": "erro",
            "mensagem": "Não foi possível consultar os agendamentos."
        }), 500