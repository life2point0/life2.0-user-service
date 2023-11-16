"""Changed current_location to current_place and standardized foreign_key names

Revision ID: c9161c13b9bc
Revises: d716ed3000bc
Create Date: 2023-11-16 21:28:59.360970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9161c13b9bc'
down_revision: Union[str, None] = 'd716ed3000bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing foreign key constraint
    op.drop_constraint('users_current_location_id_fkey', 'users', type_='foreignkey')
    
    # Rename the column
    op.alter_column('users', 'current_location_id', new_column_name='current_place_id')
    
    # Add a new foreign key constraint with the renamed column and standardized name
    op.create_foreign_key('fk__users__current_place_id', 'users', 'places', ['current_place_id'], ['id'])


def downgrade() -> None:
    # Drop the new foreign key constraint
    op.drop_constraint('fk__users__current_place_id', 'users', type_='foreignkey')

    # Revert the column name to the original
    op.alter_column('users', 'current_place_id', new_column_name='current_location_id')
    
    # Add the original foreign key constraint back with its original name
    op.create_foreign_key('users_current_location_id_fkey', 'users', 'places', ['current_location_id'], ['id'])
