from database import Base

from typing import Optional
from sqlalchemy import DECIMAL, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Salas(Base):
    __tablename__ = 'salas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    predio: Mapped[Optional[str]] = mapped_column(String(100))
    codigo: Mapped[Optional[str]] = mapped_column(String(100))

    ar_cadastrados: Mapped[list['ArCadastrados']] = relationship('ArCadastrados', back_populates='salas')