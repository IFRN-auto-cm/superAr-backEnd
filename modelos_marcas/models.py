from comandos.models import Comandos
from ar_condicionado.models import ArCadastrados

from database import Base
from sqlalchemy import DECIMAL, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ModelosMarcas(Base):
    __tablename__ = 'modelos_marcas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)

    ar_cadastrados: Mapped[list['ArCadastrados']] = relationship('ArCadastrados', back_populates='modelos_marcas')
    modelosMarcas_comando: Mapped[list['ModelosMarcasComando']] = relationship('ModelosMarcasComando', back_populates='modelos_marcas')


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