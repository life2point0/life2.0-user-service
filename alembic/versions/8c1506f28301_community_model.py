"""Community Model

Revision ID: 8c1506f28301
Revises: 55531f34a85a
Create Date: 2023-11-23 12:19:06.000455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8c1506f28301'
down_revision: Union[str, None] = '55531f34a85a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('communities',
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('photo_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', postgresql.CITEXT(), nullable=False),
    sa.Column('created_by_user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk__communities.created_by__users.id'),
    sa.ForeignKeyConstraint(['photo_id'], ['files.id'], name='fk__communities.photo_id__files.id'),
    sa.PrimaryKeyConstraint('id', name='pk__communities__id'),
    sa.UniqueConstraint('id', name='uq__communities__id'),
    sa.UniqueConstraint('name', name='uq__communities__name')
    )
    op.create_table('community_members',
    sa.Column('community_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], name='fk__community_members.community_id__communities.id'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk__community_members.user_id__users.id'),
    sa.PrimaryKeyConstraint('community_id', 'user_id', name='pk__community_members__community_id__user_id')
    )
    op.create_table('community_tagged_interests',
    sa.Column('community_id', sa.UUID(), nullable=False),
    sa.Column('interest_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], name='fk__community_tagged_interests.community_id__communities.id'),
    sa.ForeignKeyConstraint(['interest_id'], ['interests.id'], name='fk__community_tagged_interests.interest_id__interests.id'),
    sa.PrimaryKeyConstraint('community_id', 'interest_id', name='pk__community_tagged_interests__community_id__interest_id')
    )
    op.create_table('community_tagged_languages',
    sa.Column('community_id', sa.UUID(), nullable=False),
    sa.Column('language_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], name='fk__community_tagged_languages.community_id__communities.id'),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], name='fk__community_tagged_languages.language_id__languages.id'),
    sa.PrimaryKeyConstraint('community_id', 'language_id', name='pk__community_tagged_languages__community_id__language_id')
    )
    op.create_table('community_tagged_occupations',
    sa.Column('community_id', sa.UUID(), nullable=False),
    sa.Column('occupation_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], name='fk__community_tagged_occupations.community_id__communities.id'),
    sa.ForeignKeyConstraint(['occupation_id'], ['occupations.id'], name='fk__community_tagged_occupations.occupation_id__occupations.id'),
    sa.PrimaryKeyConstraint('community_id', 'occupation_id', name='pk__community_tagged_occupations__community_id__occupation_id')
    )
    op.create_table('community_tagged_places',
    sa.Column('community_id', sa.UUID(), nullable=False),
    sa.Column('place_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], name='fk__community_tagged_places.community_id__communities.id'),
    sa.ForeignKeyConstraint(['place_id'], ['places.id'], name='fk__community_tagged_places.place_id__places.id'),
    sa.PrimaryKeyConstraint('community_id', 'place_id', name='pk__community_tagged_places__community_id__place_id')
    )
    op.create_table('community_tagged_skills',
    sa.Column('community_id', sa.UUID(), nullable=False),
    sa.Column('skill_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['communities.id'], name='fk__community_tagged_skills.community_id__communities.id'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], name='fk__community_tagged_skills.skill_id__skills.id'),
    sa.PrimaryKeyConstraint('community_id', 'skill_id', name='pk__community_tagged_skills__community_id__skill_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('community_tagged_skills')
    op.drop_table('community_tagged_places')
    op.drop_table('community_tagged_occupations')
    op.drop_table('community_tagged_languages')
    op.drop_table('community_tagged_interests')
    op.drop_table('community_members')
    op.drop_table('communities')
    # ### end Alembic commands ###
