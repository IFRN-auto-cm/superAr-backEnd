from flask import Blueprint, jsonify, request, current_app
from .repository import get_db, executar_select, executar_insert, executar_insert_many, executar_update, executar_delete
import json
import redisAccess as redis
import mqtt_service_client
from mySocketio import emitir_status_ar, emitir_status_all_ar

bp = Blueprint("monitoramento", __name__)

@bp.post("/internal/mqtt/status")
def registrar_status_mqtt():
    dados = request.get_json(silent=True)
    
    if not isinstance(dados, dict):
        return jsonify({
            "erro": "Corpo da requisição deve ser um JSON"
        }), 400

    # print(dados)

    sql = """
        SELECT
            ac.id AS ar_cadastrado_id,
            s.id AS sala_id
        FROM ar_cadastrados ac
        INNER JOIN salas s
            ON s.id = ac.sala
        WHERE ac.atuador = %s;
        """

    device = dados.get("device")
    state = dados.get("state")
    sensors = dados.get("sensors")
    diagnostics = dados.get("diagnostics")
    statistics = dados.get("statistics")

    if not isinstance(device, dict) or not device.get("id"):
        return jsonify({
            "erro": "O campo atuador é obrigatório"
        }), 400

    try:
        r = executar_select(sql, (device.get("id"),),)
        if not r:
            return jsonify({"erro": "Dispositivo não cadastrado"}), 404
        sala_condicionador = r[0]

    except Exception as erro:
        current_app.logger.exception("Erro ao registrar status MQTT")

        return jsonify({
            "erro": "Não foi possível registrar o status"
        }), 500

    ar_cadastrado_id = sala_condicionador.get("ar_cadastrado_id")
    sala_id = sala_condicionador.get("sala_id")

    redis.atualizar_estado_dispositivo(
        ar_cadastrado_id,
        sala_id, 
        dados
    )

    emitir_status_ar(
        ar_cadastrado_id=ar_cadastrado_id,
        sala_id=sala_id,
        dados=dados,
    )

    return jsonify({
                "mensagem": "Status registrado",
                "resultado": sala_condicionador
            }), 201



@bp.post("/internal/mqtt/availability")
def registrar_availability():
    dados = request.get_json(silent=True)
    

    if not isinstance(dados, dict):
        return jsonify({
            "erro": "Corpo da requisição deve ser um JSON"
        }), 400

    device_id = dados.get("atuador")

    sql = """
        SELECT
            ac.id AS ar_cadastrado_id,
            s.id AS sala_id
        FROM ar_cadastrados ac
        INNER JOIN salas s
            ON s.id = ac.sala
        WHERE ac.atuador = %s;
        """

    try:
        r = executar_select(sql, (device_id,),)
        if not r:
            return jsonify({"erro": "Dispositivo não cadastrado"}), 404
        sala_condicionador = r[0]

    except Exception as erro:
        current_app.logger.exception("Erro ao registrar status MQTT")

        return jsonify({
            "erro": "Não foi possível registrar o status"
        }), 500

    ar_id = sala_condicionador.get("ar_cadastrado_id")
    sala_id = sala_condicionador.get("sala_id")
    redis.atualizar_online_offline(ar_id, sala_id, device_id, dados.get("online"))

    return jsonify({
            "mensagem": "Status registrado"
        }), 200


@bp.route("/status-ar/<int:ar_cadastrado_id>", methods=["GET"])
def enviar_status_ar(ar_cadastrado_id):

    resposta = redis.consultar_estado_dispositivo(ar_cadastrado_id)
    # print(resposta)

    return jsonify({
            "status": "ok",
            "resultado": resposta
        }), 201


@bp.route("/status-all-ar", methods=["GET"])
def enviar_status_all_ar():

    dados = redis.get_data_all_ars()

    return jsonify({
        "status": "ok",
        "mensagem": "get ars",
        "data": dados
    })


@bp.get("/teste-socket")
def teste_socket():

    ar_cadastrado_id =1
    sala_id = 10
    dados={
        "device": {
            "id": "dispositivo-teste"
        },
        "state": {
            "power": True
        },
        "sensors": {
            "temperature": 23.5
        },
        "diagnostics": {
            "RSSI": -52
        },
        "statistics": {
            "tempo_ligado": 120
        },
        "atuador": "atuador-teste",
        "topico": "teste/socket"
    }

    # emitir_status_ar(
    #     ar_cadastrado_id=ar_cadastrado_id,
    #     sala_id=sala_id,
    #     dados=dados
    # )

    emitir_status_all_ar(
        ar_cadastrado_id=ar_cadastrado_id,
        sala_id=sala_id,
        socketIO_sala="dashboard",
        dados=dados
    )

    return jsonify({
        "status": "ok",
        "mensagem": "Evento emitido"
    })
