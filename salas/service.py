from . import repository
import redisAccess


def _adicionar_dados_dashboard(sala):
    ares = sala.pop("ar_condicionados", [])
    condicionadores = []
    temperaturas = []

    for ar in ares:
        estado = redisAccess.consultar_estado_dispositivo(ar["id"])
        online = bool(estado and estado["online"])
        condicionadores.append(
            {
                "id": ar["id"],
                "nome": ar.get("nome_ar"),
                "status": "online" if online else "offline",
            }
        )
        if estado and estado.get("temperatura_medida") is not None:
            temperaturas.append(estado["temperatura_medida"])

    sala["condicionadoresAr"] = condicionadores
    sala["temperatura"] = (
        round(sum(temperaturas) / len(temperaturas), 2)
        if temperaturas
        else None
    )
    return sala


def inserir_sala(data):
    nome = data.get("nome")
    if not nome:
        raise ValueError("nome é obrigatório")

    return repository.inserir_sala(
        nome=nome,
        predio=data.get("predio"),
        codigo=data.get("codigo"),
        cod_dashboard_sala=data.get("codDashboardSala"),
    )


def lista_salas():
    try:
        resultado = repository.lista_salas_dashboard()
        return {
            "status": "ok",
            "dados": [_adicionar_dados_dashboard(sala) for sala in resultado],
        }
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}


def lista_salas_basicas():
    try:
        return {"status": "ok", "dados": repository.lista_salas()}
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}


def obter_sala(sala_id):
    sala = repository.obter_sala(sala_id)
    if sala is not None:
        sala = _adicionar_dados_dashboard(sala)
    return sala
