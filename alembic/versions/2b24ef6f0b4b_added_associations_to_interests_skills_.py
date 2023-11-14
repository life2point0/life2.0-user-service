"""Added associations to  interests, skills, occupations

Revision ID: 2b24ef6f0b4b
Revises: b78871c018c6
Create Date: 2023-11-14 12:14:32.869864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b24ef6f0b4b'
down_revision: Union[str, None] = 'b78871c018c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_skills',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('skill_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'skill_id')
    )
    op.create_unique_constraint('uq_skills_id', 'skills', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_skills_id', 'skills', type_='unique')
    op.drop_table('user_skills')
    # ### end Alembic commands ###