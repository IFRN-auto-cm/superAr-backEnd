from flask import Blueprint, jsonify, request

from . import service


bp = Blueprint("ar_condicionado", __name__)


@bp.route("/ar-cadastrados", methods=["POST"])
def inserir_ar_cadastrado():
    try:
        novo_id = service.inserir_ar_cadastrado(request.json)
        return jsonify({"status": "ok", "id": novo_id})
    except ValueError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 400
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/ar-cadastrados/<int:ar_cadastrado_id>", methods=["POST"])
def update_ar_cadastrado(ar_cadastrado_id):
    try:
        linhas_afetadas = service.atualizar_ar(
            ar_cadastrado_id,
            request.json,
        )
        return jsonify({
            "status": "ok",
            "linhas_afetadas": linhas_afetadas,
        })
    except ValueError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 400
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route(
    "/ar-cadastrados/<int:ar_cadastrado_id>/enviar-comando",
    methods=["POST"],
)
def enviar_comando_ar(ar_cadastrado_id):
    try:
        resposta = service.enviar_comando_ar(
            ar_cadastrado_id,
            request.json.get("comando_nome"),
        )
        return jsonify(resposta)
    except ValueError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 400
    except service.ComandoNaoEncontradoError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 404
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/getAddFomrArData", methods=["GET"])
def getDataToAddFormAr():
    resposta = service.obter_dados_formulario_novo()
    status_code = 200 if resposta["status"] == "ok" else 500
    return jsonify(resposta), status_code


@bp.route("/getEditFomrArData/<int:Ar_id>", methods=["GET"])
def getDataToEditFormAr(Ar_id):
    try:
        resposta = service.obter_dados_formulario_edicao(Ar_id)
        status_code = 200 if resposta["status"] == "ok" else 500
        return jsonify(resposta), status_code
    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro),
        }), 500


@bp.route("/ar-cadastrados", methods=["GET"])
def listar_ar_cadastrados():
    try:
        resultado = service.listar_ar_cadastrados()
        return jsonify({
            "status": "ok",
            "dados": resultado,
        })
    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro),
        }), 500


@bp.route("/enviar-comando/<int:ar_cadastrado_id>", methods=["GET"])
def acionar_comando(ar_cadastrado_id):
    return jsonify({
        "status": "erro",
        "mensagem": (
            "Endpoint incompleto no código original; utilize POST "
            "/ar-cadastrados/<id>/enviar-comando"
        ),
    }), 501
