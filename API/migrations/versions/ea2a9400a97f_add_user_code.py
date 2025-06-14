"""add user code

Revision ID: ea2a9400a97f
Revises: 7862e904abd2
Create Date: 2025-06-06 10:50:25.670325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea2a9400a97f'
down_revision = '7862e904abd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code', sa.Numeric(precision=6, scale=0), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('code')

    # ### end Alembic commands ###
