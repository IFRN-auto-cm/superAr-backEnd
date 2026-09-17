from flask import Blueprint, jsonify, request, current_app
from .repository import get_db, executar_select, executar_insert, executar_insert_many, executar_update, executar_delete
import json
import redisAccess as redis
import mqtt_service_client
from mySocketio import emitir_status_ar, emitir_status_all_ar
from .service import normalizar

bp = Blueprint("comandos", __name__)

@bp.route("/comandos/<int:comando_id>", methods=["DELETE"])
def deletar_comando(comando_id):
    try:
        linhas_afetadas = executar_delete(
            """
            DELETE FROM comandos
            WHERE id = %s
            """,
            (comando_id,),
        )

        if linhas_afetadas == 0:
            return jsonify({
                "status": "erro",
                "mensagem": "comando não encontrado"
            }), 404

        return jsonify({
            "status": "ok",
            "mensagem": "comando deletado com sucesso"
        })

    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro)
        }), 500


@bp.route("/comandos", methods=["POST"])
def inserir_comando():
    data = request.json

    # return jsonify({"status": "ok", "id": 1})
    nome = data.get("nome")

    if not isinstance(nome, str) or not nome.strip():
        return jsonify({"status": "erro", "mensagem": "nome é obrigatório"}), 400
    nome = normalizar(nome)

    if not nome:
        return jsonify({"status": "erro", "mensagem": "nome é obrigatório"}), 400

    sql = "INSERT INTO comandos (nome) VALUES (%s)"
    # return jsonify({"status": "ok", "id": 1})
    try:
        novo_id = executar_insert(sql, (nome,))
        return jsonify({"status": "ok", "id": novo_id})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/comandos", methods=["GET"])
def listar_comandos():
    try:
        resultado = executar_select(
            """
            SELECT id, nome
            FROM comandos
            ORDER BY nome
            """
        )

        return jsonify({"status": "ok", "dados": resultado})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500
