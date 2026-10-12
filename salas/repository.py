"""Acesso a dados da funcionalidade de salas."""
from sqlalchemy import select, text

from database import SessionLocal
from ar_condicionado.models import ArCadastrados
from modelos_marcas.models import ModelosMarcas
from .models import Salas


def inserir_sala(nome, predio, numero_de_ar, ar1, ar2, ar3, ar4):
    consulta = text(
        """
        INSERT INTO salas
        (nome, predio, numero_de_ar, ar1, ar2, ar3, ar4)
        VALUES (:nome, :predio, :numero_de_ar, :ar1, :ar2, :ar3, :ar4)
        """
    )
    with SessionLocal.begin() as session:
        resultado = session.execute(
            consulta,
            {
                "nome": nome,
                "predio": predio,
                "numero_de_ar": numero_de_ar,
                "ar1": ar1,
                "ar2": ar2,
                "ar3": ar3,
                "ar4": ar4,
            },
        )
        return resultado.lastrowid


def lista_salas():
    consulta = select(
        Salas.id,
        Salas.nome,
        Salas.codigo,
        Salas.predio,
    ).order_by(Salas.codigo, Salas.nome)
    with SessionLocal() as session:
        return [
            dict(row) for row in session.execute(consulta).mappings().all()
        ]


def obter_sala(sala_id):
    consulta_sala = select(
        Salas.id,
        Salas.nome,
        Salas.codigo,
        Salas.predio,
    ).where(Salas.id == sala_id)
    consulta_ares = (
        select(
            ArCadastrados.id,
            ArCadastrados.nome.label("nome_ar"),
            ArCadastrados.temperatura_medida,
            ArCadastrados.temperatura_referencia,
            ArCadastrados.status,
            ArCadastrados.atuador,
            ModelosMarcas.marca,
            ModelosMarcas.modelo,
        )
        .outerjoin(
            ModelosMarcas,
            ArCadastrados.modelo_marca == ModelosMarcas.id,
        )
        .where(ArCadastrados.sala == sala_id)
        .order_by(ArCadastrados.nome)
    )

    with SessionLocal() as session:
        sala = session.execute(consulta_sala).mappings().first()
        if sala is None:
            return None

        dados_sala = dict(sala)
        dados_sala["ar_condicionados"] = [
            dict(row)
            for row in session.execute(consulta_ares).mappings().all()
        ]
        return dados_sala
