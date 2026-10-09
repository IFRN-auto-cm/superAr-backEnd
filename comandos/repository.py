"""Acesso a dados da funcionalidade de comandos."""
from sqlalchemy import delete, select

from database import SessionLocal
from .models import Comandos


def inserir_comando(nome):
    with SessionLocal.begin() as session:
        comando = Comandos(nome=nome)
        session.add(comando)
        session.flush()
        return comando.id


def deletar_comando(comando_id):
    with SessionLocal.begin() as session:
        resultado = session.execute(
            delete(Comandos).where(Comandos.id == comando_id)
        )
        return resultado.rowcount


def listar_comandos():
    consulta = select(Comandos.id, Comandos.nome).order_by(Comandos.nome)
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(consulta).mappings().all()]
