"""add_unique_booking_slot_constraint

Revision ID: f3e1734ababa
Revises: 
Create Date: 2025-11-20 16:41:22.042500

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3e1734ababa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add unique constraint to prevent double-booking same package at same time
    # Only apply to active bookings (not cancelled or refunded)
    # Note: SQLite doesn't support partial indexes with WHERE clause
    # For production (PostgreSQL/MySQL), you can add the WHERE clause
    op.create_index(
        'idx_unique_booking_slot',
        'bookings',
        ['package_id', 'booking_date'],
        unique=True
    )


def downgrade():
    # Remove unique constraint
    op.drop_index('idx_unique_booking_slot', table_name='bookings')
