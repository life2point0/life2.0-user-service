"""Added languages

Revision ID: 82517ba72f01
Revises: 2b24ef6f0b4b
Create Date: 2023-11-14 12:22:23.621065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '82517ba72f01'
down_revision: Union[str, None] = '2b24ef6f0b4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('languages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', postgresql.CITEXT(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_languages_id'),
    sa.UniqueConstraint('id', name='uq_languages_id'),
    sa.UniqueConstraint('name', name='uq_languages_name')
    )
    op.create_table('user_languages',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('language_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'language_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_languages')
    op.drop_table('languages')
    # ### end Alembic commands ###
