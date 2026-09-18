from typing import Optional
import decimal

from sqlalchemy import DECIMAL, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Comandos(Base):
    __tablename__ = 'comandos'
    __table_args__ = (
        Index('uq_comandos_nome', 'nome', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    modelosMarcas_comando: Mapped[list['ModelosMarcasComando']] = relationship('ModelosMarcasComando', back_populates='comandos')


class ModelosMarcas(Base):
    __tablename__ = 'modelos_marcas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)

    ar_cadastrados: Mapped[list['ArCadastrados']] = relationship('ArCadastrados', back_populates='modelos_marcas')
    modelosMarcas_comando: Mapped[list['ModelosMarcasComando']] = relationship('ModelosMarcasComando', back_populates='modelos_marcas')


class Salas(Base):
    __tablename__ = 'salas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    predio: Mapped[Optional[str]] = mapped_column(String(100))
    codigo: Mapped[Optional[str]] = mapped_column(String(100))

    ar_cadastrados: Mapped[list['ArCadastrados']] = relationship('ArCadastrados', back_populates='salas')


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


class ModelosMarcasComando(Base):
    __tablename__ = 'modelosMarcas_comando'
    __table_args__ = (
        ForeignKeyConstraint(['comando'], ['comandos.id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_modelosmarcas_comando_comando'),
        ForeignKeyConstraint(['modelo_marcas'], ['modelos_marcas.id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_modelosmarcas_comando_modelo'),
        Index('fk_modelosmarcas_comando_comando', 'comando'),
        Index('uq_modelo_comando', 'modelo_marcas', 'comando', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    modelo_marcas: Mapped[int] = mapped_column(Integer, nullable=False)
    comando: Mapped[int] = mapped_column(Integer, nullable=False)
    comando_valor: Mapped[str] = mapped_column(String(2000), nullable=False)

    comandos: Mapped['Comandos'] = relationship('Comandos', back_populates='modelosMarcas_comando')
    modelos_marcas: Mapped['ModelosMarcas'] = relationship('ModelosMarcas', back_populates='modelosMarcas_comando')
