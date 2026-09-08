from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx

from telorax.application.dto.provisioning import ProvisioningJobDTO
from telorax.core.enums import ProvisioningState
from telorax.extensions.signup.protocol import SignupAutomation, SignupContext

if TYPE_CHECKING:
    from telorax.core.config.settings import Settings


@dataclass(frozen=True, slots=True)
class AgentConfig:
    base_url: str
    agent_id: str
    agent_token: str
    provider: str = 'android-agent'
    poll_interval_seconds: float = 5.0


class TeloraxSignupAgentClient:
    def __init__(self, config: AgentConfig) -> None:
        self._config = config

    def _headers(self) -> dict[str, str]:
        return {
            'X-Telorax-Agent-Id': self._config.agent_id,
            'X-Telorax-Agent-Token': self._config.agent_token,
        }

    async def claim(self) -> ProvisioningJobDTO | None:
        async with httpx.AsyncClient(base_url=self._config.base_url, timeout=60.0) as client:
            response = await client.post(
                '/v1/provisioning/agent/claim',
                headers=self._headers(),
                json={'provider': self._config.provider},
            )
            if response.status_code == 204:
                return None
            response.raise_for_status()
            payload = response.json()
            return ProvisioningJobDTO(
                id=int(payload['id']),
                msisdn=int(payload['msisdn']),
                state=ProvisioningState[payload['state']],
                provider=payload['provider'],
                country_iso=payload.get('country_iso'),
                first_name=payload['first_name'],
                last_name=payload['last_name'],
                two_factor_password=payload.get('two_factor_password'),
                agent_id=payload.get('agent_id'),
                account_id=payload.get('account_id'),
                failure_reason=payload.get('failure_reason'),
                metadata=dict(payload.get('metadata') or {}),
                claimed_at=payload.get('claimed_at'),
                completed_at=payload.get('completed_at'),
                created_at=payload.get('created_at'),
                updated_at=payload.get('updated_at'),
            )

    async def complete(
        self,
        job_id: int,
        session_content: bytes,
        *,
        filename: str = 'account.session',
    ) -> None:
        async with httpx.AsyncClient(base_url=self._config.base_url, timeout=120.0) as client:
            response = await client.post(
                f'/v1/provisioning/agent/jobs/{job_id}/complete',
                headers=self._headers(),
                files={'file': (filename, session_content, 'application/octet-stream')},
                data={'renew': 'true', 'ignore_2fa': 'false', 'ignore_revoke': 'false'},
            )
            response.raise_for_status()

    async def fail(self, job_id: int, reason: str) -> None:
        async with httpx.AsyncClient(base_url=self._config.base_url, timeout=60.0) as client:
            response = await client.post(
                f'/v1/provisioning/agent/jobs/{job_id}/fail',
                headers=self._headers(),
                json={'reason': reason},
            )
            response.raise_for_status()


class AndroidSignupRunner:
    """Polls telorax and delegates signup to a pluggable Android automation backend."""

    def __init__(
        self,
        client: TeloraxSignupAgentClient,
        automation: SignupAutomation,
    ) -> None:
        self._client = client
        self._automation = automation

    async def run_forever(self) -> None:
        while True:
            job = await self._client.claim()
            if job is None:
                await asyncio.sleep(self._client._config.poll_interval_seconds)
                continue
            context = SignupContext(
                msisdn=job.msisdn,
                first_name=job.first_name,
                last_name=job.last_name,
                country_iso=job.country_iso,
                two_factor_password=job.two_factor_password,
                metadata=job.metadata,
            )
            try:
                session_content = await self._automation.signup(context)
                await self._client.complete(job.id, session_content)
            except Exception as exc:
                await self._client.fail(job.id, str(exc))


def build_agent_config(settings: Settings, *, agent_id: str, base_url: str | None = None) -> AgentConfig:
    token = settings.signup_agent_token.get_secret_value() if settings.signup_agent_token else ''
    if not token:
        msg = 'SIGNUP_AGENT_TOKEN is not configured'
        raise ValueError(msg)
    host = base_url or f'http://{settings.app_host}:{settings.app_port}'
    return AgentConfig(
        base_url=host.rstrip('/'),
        agent_id=agent_id,
        agent_token=token,
        poll_interval_seconds=float(settings.signup_agent_poll_seconds),
    )
