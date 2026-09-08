"""Bootstrap schema and rename legacy operation_dispatches table."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

from telorax.infrastructure.database.models import Base

revision = '0001_rename_dispatches'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())

    if 'operation_dispatches' in tables and 'dispatches' not in tables:
        op.rename_table('operation_dispatches', 'dispatches')
        tables.remove('operation_dispatches')
        tables.add('dispatches')

    Base.metadata.create_all(bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())

    if 'dispatches' in tables and 'operation_dispatches' not in tables:
        op.rename_table('dispatches', 'operation_dispatches')
