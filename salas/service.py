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
    )


def lista_salas():
    try:
        resultado = repository.lista_salas()
        return {"status": "ok", "dados": resultado}
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}
