"""empty message

Revision ID: 4d2c9d5a23eb
Revises: 1612bad75e38
Create Date: 2020-02-20 13:52:49.243621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d2c9d5a23eb'
down_revision = '1612bad75e38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('token', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'token')
    # ### end Alembic commands ###
