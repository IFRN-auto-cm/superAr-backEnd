
from modelos_marcas.models import ModelosMarcasComando
from database import Base
from sqlalchemy import DECIMAL, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Comandos(Base):
    __tablename__ = 'comandos'
    __table_args__ = (
        Index('uq_comandos_nome', 'nome', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    modelosMarcas_comando: Mapped[list['ModelosMarcasComando']] = relationship('ModelosMarcasComando', back_populates='comandos')

