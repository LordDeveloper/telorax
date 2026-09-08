"""Rename operation_dispatches table to dispatches."""

from __future__ import annotations

from alembic import op

revision = '0001_rename_dispatches'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('operation_dispatches', 'dispatches')


def downgrade() -> None:
    op.rename_table('dispatches', 'operation_dispatches')
