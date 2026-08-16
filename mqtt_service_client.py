import logging
import os

import requests

logger = logging.getLogger(__name__)


# ============================================================
# Configuração
# ============================================================

MQTT_SERVICE_URL = os.getenv(
  "MQTT_SERVICE_URL",
  "http://mqtt-service:5002"
)


# ============================================================
# Exceções
# ============================================================

class MQTTServiceError(Exception):
  """
  Erro de comunicação com o mqtt_service.
  """

  pass


# ============================================================
# Funções
# ============================================================

def publicar(
  topic,
  payload,
  qos=0,
  retain=False
):

    try:

        resposta = requests.post(

            f"{MQTT_SERVICE_URL}/publish",

            json={
                "topic": topic,
                "payload": payload,
                "qos": qos,
                "retain": retain
            },

            timeout=5
        )


        resposta.raise_for_status()


        return resposta.json()


    except requests.Timeout as erro:

        logger.error(
            "Timeout ao acessar mqtt_service"
        )

        raise MQTTServiceError(
            "Timeout ao acessar o serviço MQTT"
        ) from erro


    except requests.ConnectionError as erro:

        logger.error(
            "Não foi possível conectar ao mqtt_service"
        )

        raise MQTTServiceError(
            "Serviço MQTT indisponível"
        ) from erro


    except requests.HTTPError as erro:

        logger.error(
            "mqtt_service retornou erro HTTP: %s",
            erro
        )

        mensagem = (
            "mqtt_service rejeitou a publicação"
        )

        try:

            dados = erro.response.json()

            mensagem = dados.get(
                "mensagem",
                mensagem
            )

        except Exception:
            pass


        raise MQTTServiceError(
            mensagem
        ) from erro


    except requests.RequestException as erro:

        logger.exception(
            "Erro ao acessar mqtt_service"
        )

        raise MQTTServiceError(
            "Erro de comunicação com o serviço MQTT"
        ) from erro

def publicar_comando_ar( atuador, payload ):

  """
  Solicita ao mqtt_service que publique
  um comando destinado a um ar-condicionado.

  A API NÃO conhece o tópico MQTT.
  """

  try:
    resposta = requests.post(

      f"{MQTT_SERVICE_URL}/ar/comando",

      json={
        "atuador": atuador,
        "payload": payload
      },

      timeout=5
    )
    resposta.raise_for_status()

    return resposta.json()

  except requests.Timeout as erro:
    raise MQTTServiceError(
      "Timeout ao acessar o serviço MQTT"
    ) from erro

  except requests.ConnectionError as erro:
    raise MQTTServiceError(
      "Serviço MQTT indisponível"
    ) from erro

  except requests.HTTPError as erro:
    mensagem = (
      "Não foi possível publicar "
      "o comando MQTT"
    )

    try:
      dados = erro.response.json()

      mensagem = dados.get(
          "mensagem",
          mensagem
      )

    except Exception:
      pass

    raise MQTTServiceError(
      mensagem
    ) from erro

  except requests.RequestException as erro:
    raise MQTTServiceError(
      "Erro de comunicação com "
      "o serviço MQTT"
    ) from erro

def verificar_status():

  try:
    resposta = requests.get(
      f"{MQTT_SERVICE_URL}/health",
      timeout=3
    )

    resposta.raise_for_status()

    return resposta.json()

  except requests.RequestException as erro:
    raise MQTTServiceError(
      "mqtt_service indisponível"
    ) from erro