from flask import Blueprint, jsonify, request

from . import service

bp = Blueprint("comandos", __name__)


@bp.route("/comandos/<int:comando_id>", methods=["DELETE"])
def deletar_comando(comando_id):
    try:
        linhas_afetadas = service.deletar_comando(comando_id)

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
    try:
        novo_id = service.inserir_comando(request.json)
        return jsonify({"status": "ok", "id": novo_id})

    except ValueError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 400
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/comandos", methods=["GET"])
def listar_comandos():
    try:
        resultado = service.listar_comandos()

        return jsonify({"status": "ok", "dados": resultado})

    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500
