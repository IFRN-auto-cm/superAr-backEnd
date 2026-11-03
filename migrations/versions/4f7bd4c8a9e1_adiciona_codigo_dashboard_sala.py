"""Adiciona o código usado para identificar a sala no dashboard."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4f7bd4c8a9e1"
down_revision: Union[str, Sequence[str], None] = "2c2cf9f84cb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    colunas = {
        coluna["name"]
        for coluna in sa.inspect(op.get_bind()).get_columns("salas")
    }
    if "codDashboardSala" not in colunas:
        op.add_column(
            "salas",
            sa.Column("codDashboardSala", sa.String(length=100), nullable=True),
        )


def downgrade() -> None:
    colunas = {
        coluna["name"]
        for coluna in sa.inspect(op.get_bind()).get_columns("salas")
    }
    if "codDashboardSala" in colunas:
        op.drop_column("salas", "codDashboardSala")
