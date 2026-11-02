"""Acesso a dados da funcionalidade de salas."""
from sqlalchemy import select, text

from database import SessionLocal
from ar_condicionado.models import ArCadastrados
from modelos_marcas.models import ModelosMarcas
from .models import Salas


def inserir_sala(nome, predio, codigo, cod_dashboard_sala):
    consulta = text(
        """
        INSERT INTO salas
        (nome, predio, codigo, codDashboardSala)
        VALUES (:nome, :predio, :codigo, :cod_dashboard_sala)
        """
    )
    with SessionLocal.begin() as session:
        resultado = session.execute(
            consulta,
            {
                "nome": nome,
                "predio": predio,
                "codigo": codigo,
                "cod_dashboard_sala": cod_dashboard_sala,
            },
        )
        return resultado.lastrowid


def lista_salas():
    consulta = select(
        Salas.id,
        Salas.nome,
        Salas.codigo,
        Salas.predio,
        Salas.cod_dashboard_sala.label("codDashboardSala"),
    ).order_by(Salas.codigo, Salas.nome)
    with SessionLocal() as session:
        return [
            dict(row) for row in session.execute(consulta).mappings().all()
        ]


def lista_salas_dashboard():
    consulta = select(
        Salas.id,
        Salas.nome,
        Salas.codigo,
        Salas.predio,
        Salas.cod_dashboard_sala.label("codDashboardSala"),
        ArCadastrados.id.label("ar_id"),
        ArCadastrados.nome.label("nome_ar"),
    ).outerjoin(
        ArCadastrados,
        ArCadastrados.sala == Salas.id,
    ).order_by(Salas.codigo, Salas.nome, ArCadastrados.nome)
    with SessionLocal() as session:
        salas = {}
        for row in session.execute(consulta).mappings():
            sala = salas.setdefault(
                row["id"],
                {
                    "id": row["id"],
                    "nome": row["nome"],
                    "codigo": row["codigo"],
                    "predio": row["predio"],
                    "codDashboardSala": row["codDashboardSala"],
                    "ar_condicionados": [],
                },
            )
            if row["ar_id"] is not None:
                sala["ar_condicionados"].append(
                    {"id": row["ar_id"], "nome_ar": row["nome_ar"]}
                )
        return list(salas.values())


def obter_sala(sala_id):
    consulta_sala = select(
        Salas.id,
        Salas.nome,
        Salas.codigo,
        Salas.predio,
        Salas.cod_dashboard_sala.label("codDashboardSala"),
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
