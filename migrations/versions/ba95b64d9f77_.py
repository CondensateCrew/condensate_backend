"""empty message

Revision ID: ba95b64d9f77
Revises: 9752a97c9e98
Create Date: 2020-02-25 15:21:21.125209

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba95b64d9f77'
down_revision = '9752a97c9e98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_actions',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['actions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'action_id')
    )
    op.create_table('user_categories',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'category_id')
    )
    op.drop_constraint('actions_user_id_fkey', 'actions', type_='foreignkey')
    op.drop_column('actions', 'user_id')
    op.drop_constraint('categories_user_id_fkey', 'categories', type_='foreignkey')
    op.drop_column('categories', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('categories', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('categories_user_id_fkey', 'categories', 'users', ['user_id'], ['id'])
    op.add_column('actions', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('actions_user_id_fkey', 'actions', 'users', ['user_id'], ['id'])
    op.drop_table('user_categories')
    op.drop_table('user_actions')
    # ### end Alembic commands ###
