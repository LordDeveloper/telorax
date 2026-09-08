from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from telorax.application.dto.account import ImportSessionDTO
from telorax.application.dto.provisioning import (
    CompleteProvisioningJobDTO,
    CreateProvisioningJobDTO,
    ProvisioningJobDTO,
)
from telorax.core.enums import ProvisioningState
from telorax.core.exceptions import OperationValidationError
from telorax.domain.entities import ProvisioningJob
from telorax.infrastructure.database.repositories.unit_of_work import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from telorax.application.services.account_service import AccountService


class ProvisioningJobNotFoundError(Exception):
    def __init__(self, job_id: int) -> None:
        super().__init__(f'Provisioning job {job_id} not found')
        self.job_id = job_id


class ProvisioningService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        account_service: AccountService,
    ) -> None:
        self._session_factory = session_factory
        self._account_service = account_service

    async def create_job(self, dto: CreateProvisioningJobDTO) -> ProvisioningJobDTO:
        if dto.msisdn <= 0:
            msg = 'msisdn must be a positive integer'
            raise OperationValidationError(msg)
        if not dto.first_name.strip() or not dto.last_name.strip():
            msg = 'first_name and last_name are required'
            raise OperationValidationError(msg)
        job = ProvisioningJob(
            id=0,
            msisdn=dto.msisdn,
            state=ProvisioningState.QUEUED,
            provider=dto.provider,
            country_iso=dto.country_iso,
            first_name=dto.first_name.strip(),
            last_name=dto.last_name.strip(),
            two_factor_password=dto.two_factor_password,
            agent_id=None,
            account_id=None,
            failure_reason=None,
            metadata=dict(dto.metadata or {}),
            claimed_at=None,
            completed_at=None,
            created_at=None,
            updated_at=None,
        )
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            created = await unit_of_work.provisioning_jobs.create(job)
            await unit_of_work.commit()
            return _to_dto(created)

    async def list_jobs(
        self,
        *,
        state: ProvisioningState | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProvisioningJobDTO]:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            jobs = await unit_of_work.provisioning_jobs.list_jobs(
                state=state,
                limit=limit,
                offset=offset,
            )
        return [_to_dto(job) for job in jobs]

    async def get_job(self, job_id: int) -> ProvisioningJobDTO | None:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            job = await unit_of_work.provisioning_jobs.get_by_id(job_id)
            return _to_dto(job) if job else None

    async def claim_next_job(self, *, provider: str, agent_id: str) -> ProvisioningJobDTO | None:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            job = await unit_of_work.provisioning_jobs.claim_next(
                provider=provider,
                agent_id=agent_id,
            )
            if job is None:
                return None
            await unit_of_work.commit()
            return _to_dto(job)

    async def complete_job(
        self,
        job_id: int,
        *,
        agent_id: str,
        session_content: bytes,
        options: CompleteProvisioningJobDTO,
    ) -> ProvisioningJobDTO:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            job = await unit_of_work.provisioning_jobs.get_by_id(job_id)
            if job is None:
                raise ProvisioningJobNotFoundError(job_id)
            if job.state is not ProvisioningState.CLAIMED or job.agent_id != agent_id:
                msg = 'Job is not claimed by this agent'
                raise OperationValidationError(msg)

        import_result = await self._account_service.import_session(
            session_content,
            ImportSessionDTO(
                password=job.two_factor_password,
                ignore_revoke=options.ignore_revoke,
                ignore_2fa=options.ignore_2fa,
                renew=options.renew,
            ),
        )
        now = datetime.now(tz=UTC)
        completed = ProvisioningJob(
            id=job.id,
            msisdn=job.msisdn,
            state=ProvisioningState.COMPLETED,
            provider=job.provider,
            country_iso=job.country_iso,
            first_name=job.first_name,
            last_name=job.last_name,
            two_factor_password=job.two_factor_password,
            agent_id=job.agent_id,
            account_id=import_result.account.id,
            failure_reason=None,
            metadata=job.metadata,
            claimed_at=job.claimed_at,
            completed_at=now,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            saved = await unit_of_work.provisioning_jobs.update(completed)
            await unit_of_work.commit()
            return _to_dto(saved)

    async def fail_job(self, job_id: int, *, agent_id: str, reason: str) -> ProvisioningJobDTO:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            job = await unit_of_work.provisioning_jobs.get_by_id(job_id)
            if job is None:
                raise ProvisioningJobNotFoundError(job_id)
            if job.state is not ProvisioningState.CLAIMED or job.agent_id != agent_id:
                msg = 'Job is not claimed by this agent'
                raise OperationValidationError(msg)
            failed = ProvisioningJob(
                id=job.id,
                msisdn=job.msisdn,
                state=ProvisioningState.FAILED,
                provider=job.provider,
                country_iso=job.country_iso,
                first_name=job.first_name,
                last_name=job.last_name,
                two_factor_password=job.two_factor_password,
                agent_id=job.agent_id,
                account_id=job.account_id,
                failure_reason=reason,
                metadata=job.metadata,
                claimed_at=job.claimed_at,
                completed_at=datetime.now(tz=UTC),
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            saved = await unit_of_work.provisioning_jobs.update(failed)
            await unit_of_work.commit()
            return _to_dto(saved)


def _to_dto(job: ProvisioningJob) -> ProvisioningJobDTO:
    return ProvisioningJobDTO(
        id=job.id,
        msisdn=job.msisdn,
        state=job.state,
        provider=job.provider,
        country_iso=job.country_iso,
        first_name=job.first_name,
        last_name=job.last_name,
        agent_id=job.agent_id,
        account_id=job.account_id,
        failure_reason=job.failure_reason,
        metadata=job.metadata,
        claimed_at=job.claimed_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
