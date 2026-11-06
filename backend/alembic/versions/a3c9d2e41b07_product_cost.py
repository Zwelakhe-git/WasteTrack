"""product cost and waste unit_cost

Revision ID: a3c9d2e41b07
Revises: 1f8e2ee31129
Create Date: 2026-11-06 16:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3c9d2e41b07'
down_revision: Union[str, None] = '1f8e2ee31129'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Себестоимость единицы продукта (руб.)
    op.add_column(
        'products',
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
    )
    # Себестоимость единицы, зафиксированная в момент списания
    op.add_column(
        'waste_records',
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('waste_records', 'unit_cost')
    op.drop_column('products', 'cost')
