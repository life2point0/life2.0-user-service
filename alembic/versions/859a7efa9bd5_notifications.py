"""Notifications

Revision ID: 859a7efa9bd5
Revises: 71b294f43612
Create Date: 2023-12-27 18:18:47.438356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '859a7efa9bd5'
down_revision: Union[str, None] = '71b294f43612'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notifications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('target_user_id', sa.UUID(), nullable=False),
    sa.Column('is_read', sa.BOOLEAN(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], name='fk__notifications.target_user_id__users.id'),
    sa.PrimaryKeyConstraint('id', name='pk__notifications__id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notifications')
    # ### end Alembic commands ###