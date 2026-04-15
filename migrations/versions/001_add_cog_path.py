"""Add cog_path column to projects table.

Revision ID: 001_add_cog_path
Revises: 
Create Date: 2026-03-31 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_cog_path'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add cog_path column to projects table
    op.add_column('projects', sa.Column('cog_path', sa.String(500), nullable=True))


def downgrade():
    # Remove cog_path column from projects table
    op.drop_column('projects', 'cog_path')
