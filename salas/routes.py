from flask import Blueprint, jsonify, request

from . import service

bp = Blueprint("salas", __name__)


@bp.route("/salas", methods=["POST"])
def inserir_sala():
    try:
        novo_id = service.inserir_sala(request.json)
        return jsonify({"status": "ok", "id": novo_id})
    except ValueError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 400
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/salas", methods=["GET"])
def api_lista_salas():
    salas = service.lista_salas()
    status_code = 200 if salas["status"] == "ok" else 500
    return jsonify(salas), status_code
