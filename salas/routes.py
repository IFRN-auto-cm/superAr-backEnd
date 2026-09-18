from flask import Blueprint, jsonify, request, current_app
from .repository import get_db, executar_select, executar_insert, executar_insert_many, executar_update, executar_delete
import json
import redisAccess as redis
import mqtt_service_client
from mySocketio import emitir_status_ar, emitir_status_all_ar
from .service import lista_salas

bp = Blueprint("salas", __name__)

@bp.route("/salas", methods=["POST"])
def inserir_sala():
    data = request.json

    nome = data.get("nome")
    predio = data.get("predio")
    numero_de_ar = data.get("numero_de_ar", 0)
    ar1 = data.get("ar1")
    ar2 = data.get("ar2")
    ar3 = data.get("ar3")
    ar4 = data.get("ar4")

    if not nome:
        return jsonify({"status": "erro", "mensagem": "nome é obrigatório"}), 400

    try:
        novo_id = executar_insert(
            """
            INSERT INTO salas
            (nome, predio, numero_de_ar, ar1, ar2, ar3, ar4)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nome, predio, numero_de_ar, ar1, ar2, ar3, ar4),
        )

        return jsonify({"status": "ok", "id": novo_id})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/salas", methods=["GET"])
def api_lista_salas():
    salas = lista_salas()
    if(salas["status"]=="ok"):
        return jsonify(salas)
    return jsonify(salas), 500
