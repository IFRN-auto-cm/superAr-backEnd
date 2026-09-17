import re

def normalizar(texto):
    # Encontra o primeiro número na string
    numero = re.search(r'\d+', texto)

    if not numero:
        return re.sub(r'\s+', '', texto).lower()

    numero = numero.group()

    # Remove todos os números
    descricao = re.sub(r'\d+', '', texto)

    # Remove todos os espaços e converte para minúsculas
    descricao = re.sub(r'\s+', '', descricao).lower()

    return f"{descricao} {numero}"
