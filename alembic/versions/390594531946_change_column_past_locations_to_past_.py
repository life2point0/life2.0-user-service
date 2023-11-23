from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '390594531946'
down_revision = '32737c666c67'
branch_labels = None
depends_on = None

def upgrade():
    # Renaming the table from 'user_past_locations' to 'user_past_places'
    op.rename_table('user_past_locations', 'user_past_places')

def downgrade():
    # Renaming back from 'user_past_places' to 'user_past_locations'
    op.rename_table('user_past_places', 'user_past_locations')
