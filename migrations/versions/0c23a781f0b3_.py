"""empty message

Revision ID: 0c23a781f0b3
Revises: 193d98a5ed8d
Create Date: 2020-02-18 16:06:28.050770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c23a781f0b3'
down_revision = '193d98a5ed8d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('idea_categories',
    sa.Column('idea_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['idea_id'], ['ideas.id'], ),
    sa.PrimaryKeyConstraint('idea_id', 'category_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('idea_categories')
    # ### end Alembic commands ###
