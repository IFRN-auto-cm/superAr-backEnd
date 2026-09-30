from typing import Optional
import decimal
import datetime
from sqlalchemy import DECIMAL, ForeignKeyConstraint, Index, Integer, String,DateTime,Boolean,Time
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


class AgendamentosDias(Base):
    __tablename__ = 'agendamentos_dias'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    agendamento_id: Mapped[list['Agendamentos']] = relationship('Agendamentos', back_populates='id',Index=True,)
    
    dia_semana:Mapped[int] = mapped_column(Integer,Index=True,nullable=False)
class Agendamentos(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    inicio_validade:Mapped[DateTime]= mapped_column(
            DateTime,
            default=datetime.now,
            nullable=False
        )
    fim_validade:Mapped[DateTime]= mapped_column(
            DateTime,
            default=datetime.now,
            nullable=False
        )
    horacio_acionamento:Mapped[Time]= mapped_column(
            Time,
            nullable=False
        )
    criado_em:Mapped[DateTime]= mapped_column(
                DateTime,
                default=datetime.now,
                nullable=False
            )
    atualizado_em:Mapped[DateTime]= mapped_column(
                DateTime,
                default=datetime.now,
                nullable=False
            )
    
    ativo:Mapped[Boolean] = mapped_column(Boolean,nullable=False)

class AgendamentoExcecoes(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agendamento_id: Mapped[list['Agendamentos']] = relationship('Agendamentos', back_populates='id')
    
    inicio:Mapped[DateTime]= mapped_column(
        DateTime,
        default=datetime.now
    )
    fim:Mapped[DateTime]= mapped_column(
        DateTime,
        default=datetime.now
    )
class AgendamentoAcoes(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agendamento_id: Mapped[list['Agendamentos']] = relationship('Agendamentos', back_populates='id')
    comando_id: Mapped[list['Agendamentos']] = relationship('Agendamentos', back_populates='id')
    valor: Mapped[str] = mapped_column(String(100), nullable=False)
    ordem:Mapped[int] = mapped_column(Integer,nullable=False)
    ar_id:Mapped[int] = mapped_column(Integer,nullable=False)
