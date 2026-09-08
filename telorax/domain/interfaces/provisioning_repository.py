from __future__ import annotations

from typing import Protocol

from telorax.core.enums import ProvisioningState
from telorax.domain.entities import ProvisioningJob


class ProvisioningJobRepository(Protocol):
    async def get_by_id(self, job_id: int) -> ProvisioningJob | None: ...

    async def list_jobs(
        self,
        *,
        state: ProvisioningState | None = None,
        limit: int,
        offset: int,
    ) -> list[ProvisioningJob]: ...

    async def create(self, job: ProvisioningJob) -> ProvisioningJob: ...

    async def update(self, job: ProvisioningJob) -> ProvisioningJob: ...

    async def claim_next(
        self,
        *,
        provider: str,
        agent_id: str,
    ) -> ProvisioningJob | None: ...
