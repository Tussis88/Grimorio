"""character e spell tables

Revision ID: 6a2d8617768e
Revises: dffcf5bb6d07
Create Date: 2024-01-06 16:05:36.238331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a2d8617768e'
down_revision = 'dffcf5bb6d07'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('character',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('group', sa.String(length=64), nullable=True),
    sa.Column('master', sa.Boolean(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('character', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_character_group'), ['group'], unique=False)
        batch_op.create_index(batch_op.f('ix_character_name'), ['name'], unique=True)
        batch_op.create_index(batch_op.f('ix_character_user_id'), ['user_id'], unique=False)

    op.create_table('spell',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('prepared', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('id_character', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_character'], ['character.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('spell', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_spell_id_character'), ['id_character'], unique=False)
        batch_op.create_index(batch_op.f('ix_spell_name'), ['name'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('spell', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_spell_name'))
        batch_op.drop_index(batch_op.f('ix_spell_id_character'))

    op.drop_table('spell')
    with op.batch_alter_table('character', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_character_user_id'))
        batch_op.drop_index(batch_op.f('ix_character_name'))
        batch_op.drop_index(batch_op.f('ix_character_group'))

    op.drop_table('character')
    # ### end Alembic commands ###