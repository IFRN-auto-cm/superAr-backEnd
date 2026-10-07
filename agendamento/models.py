from typing import Optional
import decimal
import datetime
from sqlalchemy import (
    DECIMAL,
    ForeignKeyConstraint, 
    Index, 
    Integer, 
    String,
    DateTime,
    Boolean,
    Time,
    ForeignKey
    )
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped, 
    mapped_column, 
    relationship
    )

class Base(DeclarativeBase):
    pass

class Comandos(Base):
    __tablename__ = 'comandos'
    __table_args__ = (
        Index('uq_comandos_nome', 'nome', unique=True),
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True  
        )
    
    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False)

    agendamento_acoes: Mapped[list["AgendamentoAcoes"]] = relationship(
        "AgendamentoAcoes",
        back_populates="comando"
    )


class Agendamentos(Base):

    __tablename__ = "agendamentos"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
        )
    
    nome: Mapped[str] = mapped_column(
        String(100), 
        nullable=False)

    inicio_validade:Mapped[datetime.datetime]= mapped_column(
            DateTime,
            default=datetime.datetime.now,
            nullable=False
        )
    
    fim_validade:Mapped[datetime.datetime | None ]= mapped_column(
            DateTime,
        )
    
    horario_acionamento:Mapped[datetime.time]= mapped_column(
            Time,
            nullable=False
        )
    
    ativo:Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
        )
    
    criado_em:Mapped[datetime.datetime]= mapped_column(
                DateTime,
                default=datetime.datetime.now,
                nullable=False
            )
    atualizado_em:Mapped[datetime.datetime]= mapped_column(
                DateTime,
                default=datetime.datetime.now,
                onupdate=datetime.datetime.now,
                nullable=False
            )
    dias: Mapped[list["AgendamentosDias"]] = relationship(
        "AgendamentosDias",
        back_populates="agendamento",
        cascade="all, delete-orphan"
    )

    excecoes: Mapped[list["AgendamentoExcecoes"]] = relationship(
        "AgendamentoExcecoes",
        back_populates="agendamento",
        cascade="all, delete-orphan"
    )

    acoes: Mapped[list["AgendamentoAcoes"]] = relationship(
        "AgendamentoAcoes",
        back_populates="agendamento",
        cascade="all, delete-orphan"
    )


class AgendamentosDias(Base):

    __tablename__ = 'agendamentos_dias'

    __table_args__ = (
        Index(
            "uq_agendamento_dia_semana",
            "agendamento_id",
            "dia_semana",
            unique=True
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True)
    
    agendamento_id: Mapped[int] = mapped_column(
        ForeignKey("agendamentos.id"),
        nullable=False
)
    
    dia_semana:Mapped[int] = mapped_column(
        Integer,
        nullable=False)
    
    agendamento: Mapped["Agendamentos"] = relationship(
        "Agendamentos",
        back_populates="dias"
    )
class AgendamentoExcecoes(Base):

    __tablename__ = "agendamento_excecoes"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
        )
    
    agendamento_id: Mapped[int] = mapped_column(
        ForeignKey("agendamentos.id"),
        nullable=False
    )
    
    inicio:Mapped[datetime.datetime]= mapped_column(
        DateTime,
        nullable=False
    )
    fim:Mapped[datetime.datetime]= mapped_column(
        DateTime,
        nullable=False
    )

    agendamento: Mapped["Agendamentos"] = relationship(
        "Agendamentos",
        back_populates="excecoes"
    )
class AgendamentoAcoes(Base):

    __tablename__ = "agendamento_acoes"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True)

    agendamento_id: Mapped[int] = mapped_column(
        ForeignKey("agendamentos.id"),
        nullable=False
    )

    comando_id: Mapped[int] = mapped_column(
        ForeignKey('comandos.id'), 
        nullable=False
        )

    valor: Mapped[str] = mapped_column(
        String(100),
        nullable=False)

    ordem:Mapped[int] = mapped_column(
        Integer,
        nullable=False
        )
    
    ar_id:Mapped[int] = mapped_column(Integer,
                                      nullable=False)

    agendamento: Mapped["Agendamentos"] = relationship(
        "Agendamentos",
        back_populates="acoes"
    )

    comando: Mapped["Comandos"] = relationship(
        "Comandos",
        back_populates="agendamento_acoes"
    )

