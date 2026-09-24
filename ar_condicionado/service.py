from repository import atualizar_ar 
import mqtt_service_client

def publicar_mqtt(endereco, payload):
    return mqtt_service_client.publicar_comando_ar(
        atuador=endereco,
        payload=payload
    )

def atualizar_ar(ar_cadastrado_id, data):

    temperatura_medida = 0
    temperatura_referencia = data.get("temperatura_referencia")
    modelo_marca = data.get("marcaModeloId")
    status = data.get("status")
    atuador = data.get("atuador")
    nome = data.get("nome")
    sala = data.get("sala")

    if not modelo_marca:
        raise ValueError(
            "modelo_marca é obrigatório"
        )

    if not sala:
        raise ValueError(
            "sala é obrigatória"
        )

    linhas_afetadas = repository_atualizar_ar(
        ar_cadastrado_id=ar_cadastrado_id,
        temperatura_medida=temperatura_medida,
        temperatura_referencia=temperatura_referencia,
        modelo_marca=modelo_marca,
        status=status,
        atuador=atuador,
        nome=nome,
        sala=sala
    )

    return linhas_afetadas






