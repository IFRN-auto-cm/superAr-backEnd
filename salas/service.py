import redisAccess as redis

from . import repository


def inserir_sala(data):
    nome = data.get("nome")
    if not nome:
        raise ValueError("nome é obrigatório")

    return repository.inserir_sala(
        nome=nome,
        predio=data.get("predio"),
        numero_de_ar=data.get("numero_de_ar", 0),
        ar1=data.get("ar1"),
        ar2=data.get("ar2"),
        ar3=data.get("ar3"),
        ar4=data.get("ar4"),
        cod_dashboard_sala=data.get("codDashboardSala"),
    )


def lista_salas():
    try:
        resultado = repository.lista_salas()
        for sala in resultado:
            temperaturas = []
            condicionadores = []
            for ar in sala.pop("ar_condicionados"):
                estado = redis.consultar_estado_dispositivo(ar["id"])
                online = (
                    estado.get("online", False)
                    if estado is not None
                    else redis.consultar_disponibilidade_dispositivo(ar["id"])
                )
                condicionadores.append(
                    {
                        "nome": ar["nome"] or f"condAr{ar['id']}",
                        "status": "online" if online else "offline",
                    }
                )
                if estado is not None:
                    temperatura = estado.get("temperatura_medida")
                    if temperatura is not None:
                        temperaturas.append(float(temperatura))

            sala["condicionadoresAr"] = condicionadores
            sala["temperatura"] = (
                sum(temperaturas) / len(temperaturas)
                if temperaturas
                else None
            )
        return {"status": "ok", "dados": resultado}
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}


def obter_sala(sala_id):
    return repository.obter_sala(sala_id)
