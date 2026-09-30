from . import repository


class ModeloMarcaNaoEncontradoError(Exception):
    """Indica que o modelo de marca não existe."""


def deletar_modelo_marca(modelo_marca_id):
    linhas_afetadas = repository.deletar_modelo_marca(modelo_marca_id)
    if linhas_afetadas == 0:
        raise ModeloMarcaNaoEncontradoError("comando não encontrado")


def inserir_modelo_marca(data):
    marca = data.get("marca")
    modelo = data.get("modelo")

    if not marca or not modelo:
        raise ValueError("marca e modelo são obrigatórios")

    return repository.inserir_modelo_marca(marca, modelo)


def associar_modelo_comandos(data):
    modelo_marcas = data.get("modelo_marcas")
    comandos = data.get("comandos")

    if not modelo_marcas or not comandos:
        raise ValueError(
            "modelo_marcas e pelo menos 1 comando são obrigatórios"
        )

    associacoes = [
        (
            modelo_marcas,
            comando["id"],
            str(comando["valor"]),
        )
        for comando in comandos
    ]
    repository.associar_modelo_comandos(associacoes)


def atualizar_modelo_marca_comandos(data):
    marca = data["marcaValue"]
    modelo = data["modeloValue"]
    modelo_marcas_id = data["mmId"]
    comandos_para_remover = []
    comandos_para_salvar = []

    for comando in data["comandos"]:
        comando_id = comando["id"]
        comando_valor = comando["valor"]

        if comando_valor is None:
            comandos_para_remover.append(comando_id)
        else:
            comandos_para_salvar.append(
                (modelo_marcas_id, comando_id, str(comando_valor))
            )

    repository.atualizar_modelo_marca_comandos(
        marca=marca,
        modelo=modelo,
        modelo_marcas_id=modelo_marcas_id,
        comandos_para_remover=comandos_para_remover,
        comandos_para_salvar=comandos_para_salvar,
    )


def listar_modelos_marcas():
    try:
        resultado = repository.listar_modelos_marcas()
        return {"status": "ok", "dados": resultado}
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}


def obter_dados_edicao_modelo_marca(modelo_marca_id):
    marca_modelo, comandos = repository.buscar_dados_edicao_modelo_marca(
        modelo_marca_id
    )
    return {
        "marcaModelo": marca_modelo[0],
        "comandos": comandos,
        "status": "ok",
    }


def listar_comandos_por_modelo_marca(modelo_marca_id):
    return repository.listar_comandos_por_modelo_marca(modelo_marca_id)
