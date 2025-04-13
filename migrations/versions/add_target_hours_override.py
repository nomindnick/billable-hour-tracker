"""Add target_hours_override column

Revision ID: add_target_hours_override
Revises: 593cb649810a
Create Date: 2025-04-12 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_target_hours_override'
down_revision = '593cb649810a'
branch_labels = None
depends_on = None


def upgrade():
    # This migration is actually not needed because target_hours_override was
    # already included in the initial migration (593cb649810a)
    # We're keeping this file for reference in case we need to add more columns later
    pass


def downgrade():
    pass