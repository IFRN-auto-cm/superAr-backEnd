"""Regras e operações reutilizáveis da funcionalidade de monitoramento."""
import redisAccess as redis

from mySocketio import emitir_status_all_ar, emitir_status_ar

from . import repository


class DispositivoNaoEncontradoError(Exception):
    """Indica que o atuador recebido não está cadastrado."""


def _buscar_dispositivo(atuador):
    resultado = repository.buscar_dispositivo_por_atuador(atuador)
    if not resultado:
        raise DispositivoNaoEncontradoError("Dispositivo não cadastrado")
    return resultado[0]


def registrar_status_mqtt(dados):
    if not isinstance(dados, dict):
        raise ValueError("Corpo da requisição deve ser um JSON")

    device = dados.get("device")
    if not isinstance(device, dict) or not device.get("id"):
        raise ValueError("O campo atuador é obrigatório")

    sala_condicionador = _buscar_dispositivo(device["id"])
    ar_cadastrado_id = sala_condicionador["ar_cadastrado_id"]
    sala_id = sala_condicionador["sala_id"]

    redis.atualizar_estado_dispositivo(ar_cadastrado_id, sala_id, dados)
    emitir_status_ar(
        ar_cadastrado_id=ar_cadastrado_id,
        sala_id=sala_id,
        dados=dados,
    )

    return sala_condicionador


def registrar_availability(dados):
    if not isinstance(dados, dict):
        raise ValueError("Corpo da requisição deve ser um JSON")

    device_id = dados.get("atuador")
    sala_condicionador = _buscar_dispositivo(device_id)
    ar_id = sala_condicionador["ar_cadastrado_id"]
    sala_id = sala_condicionador["sala_id"]

    redis.atualizar_online_offline(
        ar_id,
        sala_id,
        device_id,
        dados.get("online"),
    )

    return sala_condicionador


def consultar_status_ar(ar_cadastrado_id):
    return redis.consultar_estado_dispositivo(ar_cadastrado_id)


def consultar_status_todos_ars():
    return redis.get_data_all_ars()


def emitir_status_teste():
    dados = {
        "device": {
            "id": "dispositivo-teste",
        },
        "state": {
            "power": True,
        },
        "sensors": {
            "temperature": 23.5,
        },
        "diagnostics": {
            "RSSI": -52,
        },
        "statistics": {
            "tempo_ligado": 120,
        },
        "atuador": "atuador-teste",
        "topico": "teste/socket",
    }

    emitir_status_all_ar(
        ar_cadastrado_id=1,
        sala_id=10,
        socketIO_sala="dashboard",
        dados=dados,
    )
