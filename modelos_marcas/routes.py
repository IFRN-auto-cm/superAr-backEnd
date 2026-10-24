from flask import Blueprint, jsonify, request

from . import service


bp = Blueprint("modelos_marcas", __name__)


@bp.route("/modelos-marcas/<int:marcaModelo_id>", methods=["DELETE"])
def deletar_marcaModelo(marcaModelo_id):
    try:
        service.deletar_modelo_marca(marcaModelo_id)
        return jsonify({
            "status": "ok",
            "mensagem": "comando deletado com sucesso",
        })
    except service.ModeloMarcaNaoEncontradoError as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro),
        }), 404
    except Exception as erro:
        return jsonify({
            "status": "erro",
            "mensagem": str(erro),
        }), 500


@bp.route("/modelos-marcas", methods=["POST"])
def inserir_modelo_marca():
    try:
        novo_id = service.inserir_modelo_marca(request.json)
        return jsonify({"status": "ok", "id": novo_id})
    except ValueError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 400
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/modelos-marcas-comandos", methods=["POST"])
def associar_modelo_comando():
    try:
        service.associar_modelo_comandos(request.json)
        return jsonify({"status": "ok"})
    except ValueError as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 400
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/updateModelosComando", methods=["POST"])
def updateModelosComando():
    try:
        service.atualizar_modelo_marca_comandos(request.json)
        return jsonify({"status": "ok"})
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/modelos-marcas", methods=["GET"])
def api_listar_modelos_marcas():
    resposta = service.listar_modelos_marcas()
    status_code = 200 if resposta["status"] == "ok" else 500
    return jsonify(resposta), status_code


@bp.route("/edite-modelos-marcas/<int:modelo_marca_id>", methods=["GET"])
def listar_modelos_marcas1(modelo_marca_id):
    try:
        resposta = service.obter_dados_edicao_modelo_marca(modelo_marca_id)
        return jsonify(resposta)
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500


@bp.route("/modelos-marcas/<int:modelo_marca_id>/comandos", methods=["GET"])
def listar_comandos_por_modelo_marca(modelo_marca_id):
    try:
        dados = service.listar_comandos_por_modelo_marca(modelo_marca_id)
        return jsonify({"status": "ok", "dados": dados})
    except Exception as erro:
        return jsonify({"status": "erro", "mensagem": str(erro)}), 500
