"""reason requires_comment + default reason «Прочее»

Revision ID: b7e4f1c8d259
Revises: a3c9d2e41b07
Create Date: 2026-11-18 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7e4f1c8d259'
down_revision: Union[str, None] = 'a3c9d2e41b07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'reasons',
        sa.Column('requires_comment', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Уже существующие «Прочее»/«Другое» начинают требовать комментарий
    op.execute(
        "UPDATE reasons SET requires_comment = true "
        "WHERE lower(name) IN ('прочее', 'другое', 'иное')"
    )
    # Причина «Прочее» есть в справочнике всегда
    op.execute(
        "INSERT INTO reasons (name, description, status, requires_comment) "
        "SELECT 'Прочее', 'Причина не из списка — опишите в комментарии', 'active', true "
        "WHERE NOT EXISTS (SELECT 1 FROM reasons WHERE lower(name) = 'прочее')"
    )


def downgrade() -> None:
    op.drop_column('reasons', 'requires_comment')
