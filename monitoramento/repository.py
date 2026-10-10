"""Acesso a dados da funcionalidade de monitoramento."""
from sqlalchemy import select

from ar_condicionado.models import ArCadastrados
from database import SessionLocal
from salas.models import Salas


def buscar_dispositivo_por_atuador(atuador):
    consulta = (
        select(
            ArCadastrados.id.label("ar_cadastrado_id"),
            Salas.id.label("sala_id"),
        )
        .join(Salas, Salas.id == ArCadastrados.sala)
        .where(ArCadastrados.atuador == atuador)
    )
    with SessionLocal() as session:
        return [
            dict(row) for row in session.execute(consulta).mappings().all()
        ]
