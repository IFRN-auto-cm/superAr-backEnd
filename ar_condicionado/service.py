import json
from urllib import request

import mqtt_service_client
import redisAccess as redis
from modelos_marcas.service import listar_modelos_marcas
from salas.service import lista_salas

from models import ArCadastrados

from . import repository


class ComandoNaoEncontradoError(Exception):
    """Indica que o comando não está cadastrado para o aparelho."""


def publicar_mqtt(endereco, payload):
    return mqtt_service_client.publicar_comando_ar(
        atuador=endereco,
        payload=payload,
    )


def inserir_ar_cadastrado():
    data = request.get.json or {}

    temperatura_referencia = data.get("temperatura_referencia")
    modelo_marca = data.get("marcaModeloId")
    status = data.get("status")
    atuador = data.get("atuador")
    nome = data.get("nome")
    sala = data.get("sala")

    if not modelo_marca:
        return jsonify({
            "status": "erro",
            "mensagem": "modelo_marca é obrigatório"
        }), 400


    
    # modelo_marca = data.get("marcaModeloId")
    # if not modelo_marca:
    #     raise ValueError("modelo_marca é obrigatório")

    # return repository.inserir_ar_cadastrado(
    #     temperatura_referencia=data.get("temperatura_referencia"),
    #     modelo_marca=modelo_marca,
    #     status=data.get("status"),
    #     atuador=data.get("atuador"),
    #     nome=data.get("nome"),
    #     sala=data.get("sala"),
    # )


def atualizar_ar(ar_cadastrado_id, data):
    modelo_marca = data.get("marcaModeloId")
    sala = data.get("sala")

    if not modelo_marca:
        raise ValueError("modelo_marca é obrigatório")
    if not sala:
        raise ValueError("sala é obrigatória")

    return repository.atualizar_ar_cadastrado(
        ar_cadastrado_id=ar_cadastrado_id,
        temperatura_medida=0,
        temperatura_referencia=data.get("temperatura_referencia"),
        modelo_marca=modelo_marca,
        status=data.get("status"),
        atuador=data.get("atuador"),
        nome=data.get("nome"),
        sala=sala,
    )


def enviar_comando_ar(ar_cadastrado_id, comando_nome):
    if not comando_nome:
        raise ValueError("comando_nome é obrigatório")

    resultado = repository.buscar_comando_ar(ar_cadastrado_id, comando_nome)
    if not resultado:
        raise ComandoNaoEncontradoError(
            "Comando não cadastrado para o modelo deste ar-condicionado"
        )

    dados = resultado[0]
    if not dados["atuador"]:
        raise ValueError("Este ar-condicionado não possui atuador cadastrado")

    vetor = json.loads(dados["comando_valor"])
    comando_normalizado = comando_nome.casefold()
    referencia = 0

    if comando_normalizado == "desligar":
        tipo_comando = "desligar"
    elif comando_normalizado.split()[0] == "ligar":
        partes_comando = comando_nome.split()
        if len(partes_comando) < 2:
            raise ValueError("O comando ligar precisa informar a referência")
        tipo_comando = "ligar"
        referencia = partes_comando[1]
    else:
        raise ValueError("Comando não suportado")

    payload = {
        "irCmd": vetor,
        "length": len(vetor),
        "cmdType": tipo_comando,
        "ref": referencia,
    }
    endereco_atuador = dados["atuador"]
    publicar_mqtt(endereco_atuador, payload)

    return {
        "status": "ok",
        "mensagem": "Comando enviado com sucesso",
        "endereco": endereco_atuador,
        "payload": payload,
    }


def obter_dados_formulario_novo():
    salas = lista_salas()
    marca_modelo = listar_modelos_marcas()

    if salas["status"] != "ok":
        return salas
    if marca_modelo["status"] != "ok":
        return marca_modelo

    return {
        "status": "ok",
        "salas": salas["dados"],
        "marcaModelo": marca_modelo["dados"],
    }


def obter_dados_formulario_edicao(ar_cadastrado_id):
    salas = lista_salas()
    marca_modelo = listar_modelos_marcas()

    if salas["status"] != "ok":
        return salas
    if marca_modelo["status"] != "ok":
        return marca_modelo

    resultado = repository.buscar_ar_para_edicao(ar_cadastrado_id)
    dados = {
        "editAr": resultado,
        "salas": salas["dados"],
        "marcasModelos": marca_modelo["dados"],
    }

    return {"status": "ok", "dados": dados}


def listar_ar_cadastrados():
    resultado = repository.listar_ar_cadastrados()

    for ar in resultado:
        status_ar = redis.consultar_estado_dispositivo(ar["id"])
        if status_ar is not None:
            ar["temperatura_medida"] = status_ar["temperatura_medida"]
            ar["status"] = "ligado" if status_ar["power"] else "desligado"
        else:
            ar["status"] = "desconhecido"
            ar["temperatura_medida"] = "desconhecido"

    return resultado
