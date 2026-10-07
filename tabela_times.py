from sqlalchemy import Interger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Campeonato(Base):
    __tablename__ = "campeonato"

    id: Mapped[int] = mapped_column(
        Interger,
        primary_key=True,
        autoincrement=True
    )

    nome_time: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )

    pontuacao: Mapped[int] = mapped_column(
        Interger,
        nullable=False
    )