"""enums

Revision ID: a661ccb20bad
Revises: e28aa2d3a4c7
Create Date: 2026-03-05 19:15:22.567173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a661ccb20bad'
down_revision: Union[str, Sequence[str], None] = 'e28aa2d3a4c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Manually create the ENUM type in the database
    order_status = sa.Enum('pending', 'paid', 'shipped', 'delivered', 'cancelled', name='orderstatus')
    order_status.create(op.get_bind(), checkfirst=True)

    # 2. Now run the alter_column (Alembic should already have this part)
    op.alter_column('orders', 'status',
               existing_type=sa.VARCHAR(),
               type_=order_status,
               postgresql_using="status::orderstatus", # Added this to help with the conversion
               existing_nullable=True)


def downgrade() -> None:
    # 1. Change the column back to VARCHAR
    op.alter_column('orders', 'status',
               existing_type=sa.Enum('pending', 'paid', 'shipped', 'delivered', 'cancelled', name='orderstatus'),
               type_=sa.VARCHAR(),
               existing_nullable=True)

    # 2. Manually drop the ENUM type
    sa.Enum(name='orderstatus').drop(op.get_bind(), checkfirst=True)
