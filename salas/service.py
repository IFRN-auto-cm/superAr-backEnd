from . import repository
import redisAccess
import math


def _temperatura_valida(valor):
    if valor is None:
        return None
    try:
        temperatura = float(valor)
    except (TypeError, ValueError):
        return None
    return temperatura if math.isfinite(temperatura) else None


def _adicionar_dados_dashboard(sala):
    ares = sala.pop("ar_condicionados", [])
    condicionadores = []
    temperaturas = []

    for ar in ares:
        estado = redisAccess.consultar_estado_dispositivo(ar["id"])
        online = bool(estado and estado.get("online"))
        temperatura_medida = _temperatura_valida(
            estado.get("temperatura_medida") if estado else None
        )
        temperatura_ajuste = _temperatura_valida(
            estado.get("temperatura_setpoint") if estado else None
        )
        if temperatura_ajuste is None:
            temperatura_ajuste = _temperatura_valida(
                ar.get("temperatura_referencia")
            )

        condicionadores.append(
            {
                "id": ar["id"],
                "nome": ar.get("nome_ar"),
                "status": "online" if online else "offline",
                "marca": ar.get("marca"),
                "modelo": ar.get("modelo"),
                "atuador": ar.get("atuador"),
                "temperatura_medida": temperatura_medida,
                "estado": (
                    "ligado"
                    if estado and estado.get("power") is True
                    else "desligado"
                    if estado and estado.get("power") is False
                    else "desconhecido"
                ),
                "temperatura_ajuste": temperatura_ajuste,
            }
        )
        if online and temperatura_medida is not None:
            temperaturas.append(temperatura_medida)

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


def obter_sala(sala_id=None, codigo=None, cod_dashboard_sala=None):
    sala = repository.obter_sala(
        sala_id=sala_id,
        codigo=codigo,
        cod_dashboard_sala=cod_dashboard_sala,
    )
    if sala is not None:
        sala = _adicionar_dados_dashboard(sala)
    return sala
