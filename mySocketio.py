import logging
import os
from typing import Any

from flask import request
from flask_socketio import SocketIO, join_room, leave_room

logger = logging.getLogger(__name__)

NAMESPACE = "/monitoramento"
EVENTO_STATUS_ATUALIZADO = "status_ar_atualizado"


def _origens_permitidas():
    valor = os.getenv("SOCKETIO_CORS_ORIGINS", "http://localhost:3000")
    origens = [origem.strip() for origem in valor.split(",") if origem.strip()]
    return origens or ["http://localhost:3000"]


socketio = SocketIO(
    # cors_allowed_origins=_origens_permitidas(),
    cors_allowed_origins="*",
    async_mode="threading",
    logger=False,
    engineio_logger=False,
)


def init_socketio(app):
    """Vincula a instância Socket.IO à aplicação Flask existente."""
    socketio.init_app(app)
    return socketio


def emitir_status_ar(
    *,
    ar_cadastrado_id: int,
    sala_id: int,
    dados: dict[str, Any],
) -> None:
    """Envia ao frontend o novo estado recebido via MQTT."""
    payload = {
        "ar_cadastrado_id": ar_cadastrado_id,
        "sala_id": sala_id,
        "device": dados.get("device"),
        "state": dados.get("state"),
        "sensors": dados.get("sensors"),
        "diagnostics": dados.get("diagnostics"),
        "statistics": dados.get("statistics"),
        "atuador": dados.get("atuador"),
        "topico": dados.get("topico"),
    }

    socketio.emit(
        EVENTO_STATUS_ATUALIZADO,
        payload,
        namespace=NAMESPACE,
    )

def emitir_status_all_ar(
    *,
    ar_cadastrado_id: int,
    sala_id: int,
    socketIO_sala: str,
    dados: dict[str, Any],
) -> None:
    """Envia ao frontend o novo estado recebido via MQTT."""
    payload = {
        "ar_cadastrado_id": ar_cadastrado_id,
        "sala_id": sala_id,
        "device": dados.get("device"),
        "state": dados.get("state"),
        "sensors": dados.get("sensors"),
        "diagnostics": dados.get("diagnostics"),
        "statistics": dados.get("statistics"),
        "atuador": dados.get("atuador"),
        "topico": dados.get("topico"),
    }

    socketio.emit(
        EVENTO_STATUS_ATUALIZADO,
        payload,
        room=f"sala:{socketIO_sala}",
        namespace=NAMESPACE,
    )

@socketio.on("connect", namespace=NAMESPACE)
def ao_conectar(auth=None):
    """
    Ponto preparado para validar JWT futuramente.

    Exemplo futuro:
        token = (auth or {}).get("token")
        validar_token_jwt(token)
        return False quando o token for inválido.
    """
    logger.info("Frontend conectado ao Socket.IO: %s", request.sid)


@socketio.on("disconnect", namespace=NAMESPACE)
def ao_desconectar(reason=None):
    logger.info(
        "Frontend desconectado do Socket.IO: sid=%s motivo=%s",
        request.sid,
        reason,
    )

@socketio.on("inscrever_sala", namespace=NAMESPACE)
def inscrever_sala(dados):
    sala_id = dados.get("soketIO_sala_id")

    if sala_id is None:
        socketio.emit(
            "erro_inscricao",
            {
                "mensagem": "sala_id é obrigatório"
            }
        )
        return

    room = f"sala:{sala_id}"

    join_room(room)

    print(
        f"Socket {request.sid} entrou na room {room}"
    )

    socketio.emit(
        "inscricao_confirmada",
        {
            "tipo": "sala",
            "sala_id": sala_id,
            "room": room,
        }
    )

@socketio.on("cancelar_sala", namespace=NAMESPACE)
def cancelar_sala(dados):
    sala_id = dados.get("soketIO_sala_id")

    if sala_id is None:
        return

    room = f"sala:{sala_id}"

    leave_room(room)

    print(
        f"Socket {request.sid} saiu da room {room}"
    )