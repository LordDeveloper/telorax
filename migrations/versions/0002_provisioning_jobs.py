"""Add provisioning_jobs table for automated signup orchestration."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = '0002_provisioning_jobs'
down_revision = '0001_rename_dispatches'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if 'provisioning_jobs' in tables:
        return
    op.create_table(
        'provisioning_jobs',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('msisdn', sa.BigInteger(), nullable=False),
        sa.Column('state', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('provider', sa.String(length=64), nullable=False, server_default='android-agent'),
        sa.Column('country_iso', sa.String(length=3), nullable=True),
        sa.Column('first_name', sa.String(length=64), nullable=False),
        sa.Column('last_name', sa.String(length=64), nullable=False),
        sa.Column('two_factor_password', sa.String(length=255), nullable=True),
        sa.Column('agent_id', sa.String(length=128), nullable=True),
        sa.Column('account_id', sa.BigInteger(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_provisioning_jobs_msisdn', 'provisioning_jobs', ['msisdn'])
    op.create_index('ix_provisioning_jobs_state', 'provisioning_jobs', ['state'])
    op.create_index('ix_provisioning_jobs_provider', 'provisioning_jobs', ['provider'])
    op.create_index('ix_provisioning_jobs_agent_id', 'provisioning_jobs', ['agent_id'])
    op.create_index('ix_provisioning_jobs_account_id', 'provisioning_jobs', ['account_id'])


def downgrade() -> None:
    op.drop_table('provisioning_jobs')
