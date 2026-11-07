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


@bp.route("/salas/<int:sala_id>", methods=["GET"])
def api_obter_sala(sala_id):
    return _api_obter_sala(sala_id=sala_id)


@bp.route("/salas/codigo/<string:codigo>", methods=["GET"])
def api_obter_sala_por_codigo(codigo):
    return _api_obter_sala(codigo=codigo)


@bp.route("/salas/dashboard/<string:codigo_dashboard>", methods=["GET"])
def api_obter_sala_por_codigo_dashboard(codigo_dashboard):
    return _api_obter_sala(cod_dashboard_sala=codigo_dashboard)


def _api_obter_sala(**filtros):
    try:
        sala = service.obter_sala(**filtros)
        if sala is None:
            return jsonify({
                "status": "erro",
                "mensagem": "Sala não encontrada",
            }), 404
        return jsonify({"status": "ok", "dados": sala})
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500
