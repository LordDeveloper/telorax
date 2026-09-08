from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from telorax.core.enums import ProvisioningState
from telorax.domain.entities import ProvisioningJob
from telorax.domain.interfaces.provisioning_repository import ProvisioningJobRepository
from telorax.infrastructure.database import models as schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _to_job(row: schema.ProvisioningJob) -> ProvisioningJob:
    return ProvisioningJob(
        id=row.id,
        msisdn=row.msisdn,
        state=ProvisioningState(row.state),
        provider=row.provider,
        country_iso=row.country_iso,
        first_name=row.first_name,
        last_name=row.last_name,
        two_factor_password=row.two_factor_password,
        agent_id=row.agent_id,
        account_id=row.account_id,
        failure_reason=row.failure_reason,
        metadata=row.metadata_json or {},
        claimed_at=row.claimed_at,
        completed_at=row.completed_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SQLAlchemyProvisioningJobRepository(ProvisioningJobRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, job_id: int) -> ProvisioningJob | None:
        row = await self._session.get(schema.ProvisioningJob, job_id)
        return _to_job(row) if row else None

    async def list_jobs(
        self,
        *,
        state: ProvisioningState | None = None,
        limit: int,
        offset: int,
    ) -> list[ProvisioningJob]:
        query = (
            select(schema.ProvisioningJob)
            .order_by(schema.ProvisioningJob.id.asc())
            .limit(limit)
            .offset(offset)
        )
        if state is not None:
            query = query.where(schema.ProvisioningJob.state == state.value)
        result = await self._session.execute(query)
        return [_to_job(row) for row in result.scalars()]

    async def create(self, job: ProvisioningJob) -> ProvisioningJob:
        row = schema.ProvisioningJob(
            msisdn=job.msisdn,
            state=job.state.value,
            provider=job.provider,
            country_iso=job.country_iso,
            first_name=job.first_name,
            last_name=job.last_name,
            two_factor_password=job.two_factor_password,
            metadata_json=job.metadata,
        )
        self._session.add(row)
        await self._session.flush()
        return _to_job(row)

    async def update(self, job: ProvisioningJob) -> ProvisioningJob:
        row = await self._session.get(schema.ProvisioningJob, job.id)
        if row is None:
            msg = f'Provisioning job {job.id} not found'
            raise ValueError(msg)
        row.state = job.state.value
        row.agent_id = job.agent_id
        row.account_id = job.account_id
        row.failure_reason = job.failure_reason
        row.metadata_json = job.metadata
        row.claimed_at = job.claimed_at
        row.completed_at = job.completed_at
        await self._session.flush()
        return _to_job(row)

    async def claim_next(
        self,
        *,
        provider: str,
        agent_id: str,
    ) -> ProvisioningJob | None:
        result = await self._session.execute(
            select(schema.ProvisioningJob)
            .where(schema.ProvisioningJob.state == ProvisioningState.QUEUED.value)
            .where(schema.ProvisioningJob.provider == provider)
            .order_by(schema.ProvisioningJob.id.asc())
            .limit(1)
            .with_for_update(skip_locked=True),
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        now = datetime.now(tz=UTC)
        row.state = ProvisioningState.CLAIMED.value
        row.agent_id = agent_id
        row.claimed_at = now
        await self._session.flush()
        return _to_job(row)
