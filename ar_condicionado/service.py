import mqtt_service_client

def publicar_mqtt(endereco, payload):
    return mqtt_service_client.publicar_comando_ar(
        atuador=endereco,
        payload=payload
    )
