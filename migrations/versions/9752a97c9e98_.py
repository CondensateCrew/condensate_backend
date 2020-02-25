"""empty message

Revision ID: 9752a97c9e98
Revises: 0ccb5f632c81
Create Date: 2020-02-24 11:22:50.619261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9752a97c9e98'
down_revision = '0ccb5f632c81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('actions', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('actions', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###