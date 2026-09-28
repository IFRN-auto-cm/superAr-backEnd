from typing import Optional
import decimal

from database import Base

from sqlalchemy import DECIMAL, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ArCadastrados(Base):
    __tablename__ = 'ar_cadastrados'
    __table_args__ = (
        ForeignKeyConstraint(['modelo_marca'], ['modelos_marcas.id'], ondelete='RESTRICT', onupdate='CASCADE', name='fk_ar_modelo_marca'),
        ForeignKeyConstraint(['sala'], ['salas.id'], name='fk_ar_cadastrados_sala'),
        Index('fk_ar_cadastrados_sala', 'sala'),
        Index('fk_ar_modelo_marca', 'modelo_marca')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    modelo_marca: Mapped[int] = mapped_column(Integer, nullable=False)
    temperatura_medida: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2))
    temperatura_referencia: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    atuador: Mapped[Optional[str]] = mapped_column(String(100))
    nome: Mapped[Optional[str]] = mapped_column(String(25))
    sala: Mapped[Optional[int]] = mapped_column(Integer)

    modelos_marcas: Mapped['ModelosMarcas'] = relationship('ModelosMarcas', back_populates='ar_cadastrados')
    salas: Mapped[Optional['Salas']] = relationship('Salas', back_populates='ar_cadastrados')


