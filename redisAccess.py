import redis
import os
from datetime import datetime, timezone
from typing import Any


ONLINE_TTL_SECONDS = 90

redis_client = redis.Redis(
  host=os.getenv("REDIS_HOST", "redis"),
  port=int(os.getenv("REDIS_PORT", 6379)),
  db=int(os.getenv("REDIS_DB", 0)),
  decode_responses=True
)

def teste():
  redis_client.set("teste", "Olá Redis!")
  print(redis_client.get("teste"))

def converter_booleano(valor: Any) -> str:
  return "1" if bool(valor) else "0"


def atualizar_estado_dispositivo(ar_id, sala_id, dados: dict[str, Any]) -> None:

  device = dados.get("device")
  state = dados.get("state")
  sensors = dados.get("sensors")
  diagnostics = dados.get("diagnostics")
  statistics = dados.get("statistics")

  device_id = device.get("id")

  if not device_id:
    raise ValueError("A mensagem não possui device_id")

  state_key = f"superar:device:{device_id}:state"
  online_key = f"superar:device:{device_id}:online"

  atualizado_em = datetime.now(timezone.utc).isoformat()

  estado = {
    "device_id": device_id,
    "ar_cadastrado_id": ar_id,
    "sala_id": sala_id,
    "temperatura_medida": str(sensors.get("temperature")),
    "temperatura_setpoint": str(state.get("temperaturaReferencia")),
    "power": converter_booleano(state.get("power", False)),
    "modo": str(state.get("modo", "")),
    "fan_speed": str(state.get("fan_speed", "")),
    "atualizado_em": atualizado_em,
  }

  print(estado)

  # Pipeline reduz o número de viagens entre aplicação e Redis.
  with redis_client.pipeline(transaction=True) as pipeline:
    pipeline.hset(state_key, mapping=estado)
    pipeline.set(
      online_key,
      "1",
      ex=ONLINE_TTL_SECONDS,
    )
    pipeline.execute()