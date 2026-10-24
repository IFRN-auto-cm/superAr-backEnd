from flask import Blueprint, current_app, jsonify, request

from . import service


bp = Blueprint("monitoramento", __name__)


@bp.post("/internal/mqtt/status")
def registrar_status_mqtt():
    dados = request.get_json(silent=True)

    try:
        sala_condicionador = service.registrar_status_mqtt(dados)
        return jsonify({
            "mensagem": "Status registrado",
            "resultado": sala_condicionador,
        }), 201
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    except service.DispositivoNaoEncontradoError as erro:
        return jsonify({"erro": str(erro)}), 404
    except Exception:
        current_app.logger.exception("Erro ao registrar status MQTT")
        return jsonify({"erro": "Não foi possível registrar o status"}), 500


@bp.post("/internal/mqtt/availability")
def registrar_availability():
    dados = request.get_json(silent=True)

    try:
        service.registrar_availability(dados)
        return jsonify({"mensagem": "Status registrado"}), 200
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    except service.DispositivoNaoEncontradoError as erro:
        return jsonify({"erro": str(erro)}), 404
    except Exception:
        current_app.logger.exception("Erro ao registrar disponibilidade MQTT")
        return jsonify({"erro": "Não foi possível registrar o status"}), 500


@bp.route("/status-ar/<int:ar_cadastrado_id>", methods=["GET"])
def enviar_status_ar(ar_cadastrado_id):
    resposta = service.consultar_status_ar(ar_cadastrado_id)

    return jsonify({
        "status": "ok",
        "resultado": resposta,
    }), 201


@bp.route("/status-all-ar", methods=["GET"])
def enviar_status_all_ar():
    dados = service.consultar_status_todos_ars()

    return jsonify({
        "status": "ok",
        "mensagem": "get ars",
        "data": dados,
    })


@bp.get("/teste-socket")
def teste_socket():
    service.emitir_status_teste()

    return jsonify({
        "status": "ok",
        "mensagem": "Evento emitido",
    })
