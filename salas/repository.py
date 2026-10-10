"""Acesso a dados da funcionalidade de salas."""
from sqlalchemy import select, text

from database import SessionLocal
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
