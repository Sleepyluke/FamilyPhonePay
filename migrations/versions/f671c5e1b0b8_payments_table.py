"""add payments table and paid_at column

Revision ID: f671c5e1b0b8
Revises: 4d449b07f47a
Create Date: 2025-06-06 23:50:00
"""

from alembic import op
import sqlalchemy as sa

revision = 'f671c5e1b0b8'
down_revision = '4d449b07f47a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bill_item', sa.Column('paid_at', sa.DateTime(), nullable=True))
    op.create_table(
        'payment',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('bill_item_id', sa.Integer(), sa.ForeignKey('bill_item.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('payment')
    op.drop_column('bill_item', 'paid_at')

