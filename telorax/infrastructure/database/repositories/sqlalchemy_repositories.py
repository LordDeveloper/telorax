from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import or_, select

from telorax.core.enums import AccountState, CampaignState, EngagementKind
from telorax.domain.entities import Campaign, TelegramAccount
from telorax.domain.interfaces.repositories import CampaignRepository, TelegramAccountRepository
from telorax.infrastructure.database.models import CampaignModel, TelegramAccountModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _to_account(model: TelegramAccountModel) -> TelegramAccount:
    return TelegramAccount(
        id=model.id,
        msisdn=model.msisdn,
        session_ciphertext=model.session_ciphertext,
        state=AccountState(model.state),
        country_iso=model.country_iso,
        telegram_user_id=model.telegram_user_id,
        telegram_username=model.telegram_username,
        display_name=model.display_name,
        telegram_app_id=model.telegram_app_id,
        telegram_app_hash=model.telegram_app_hash,
        two_factor_secret=model.two_factor_secret,
        reliability_score=model.reliability_score,
        rate_limited_until=model.rate_limited_until,
        restricted_until=model.restricted_until,
        last_online_at=model.last_online_at,
        two_factor_confirmed_at=model.two_factor_confirmed_at,
        foreign_sessions_revoked_at=model.foreign_sessions_revoked_at,
        last_engaged_at=model.last_engaged_at,
        account_ttl_configured=model.account_ttl_configured,
        proxy_label=model.proxy_label,
        notes=model.notes,
        provisioned_at=model.provisioned_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_campaign(model: CampaignModel) -> Campaign:
    return Campaign(
        id=model.id,
        engagement_kind=EngagementKind(model.engagement_kind),
        target_count=model.target_count,
        fulfilled_count=model.fulfilled_count,
        target_spec=model.target_spec or {},
        state=CampaignState(model.state),
        dedup_fingerprint=model.dedup_fingerprint,
        retry_attempts=model.retry_attempts,
        priority=model.priority,
        country_filter=model.country_filter,
        source_label=model.source_label,
        failure_summary=model.failure_summary,
        scheduled_at=model.scheduled_at,
        started_at=model.started_at,
        finished_at=model.finished_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyTelegramAccountRepository(TelegramAccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, account_id: int) -> TelegramAccount | None:
        model = await self._session.get(TelegramAccountModel, account_id)
        return _to_account(model) if model else None

    async def get_by_msisdn(self, msisdn: int) -> TelegramAccount | None:
        result = await self._session.execute(
            select(TelegramAccountModel).where(TelegramAccountModel.msisdn == msisdn),
        )
        model = result.scalar_one_or_none()
        return _to_account(model) if model else None

    async def list_operational(
        self,
        *,
        limit: int,
        country_iso: str | None = None,
    ) -> list[TelegramAccount]:
        now = datetime.now(tz=UTC)
        query = (
            select(TelegramAccountModel)
            .where(TelegramAccountModel.state == AccountState.ACTIVE.value)
            .where(
                or_(
                    TelegramAccountModel.rate_limited_until.is_(None),
                    TelegramAccountModel.rate_limited_until < now,
                ),
            )
            .order_by(TelegramAccountModel.reliability_score.desc())
            .limit(limit)
        )
        if country_iso:
            query = query.where(TelegramAccountModel.country_iso == country_iso)
        result = await self._session.execute(query)
        return [_to_account(model) for model in result.scalars()]

    async def update_state(self, account_id: int, state: AccountState) -> None:
        model = await self._session.get(TelegramAccountModel, account_id)
        if model:
            model.state = state.value

    async def update_reliability_score(self, account_id: int, score: int) -> None:
        model = await self._session.get(TelegramAccountModel, account_id)
        if model:
            model.reliability_score = score

    async def create(self, account: TelegramAccount) -> TelegramAccount:
        model = TelegramAccountModel(
            msisdn=account.msisdn,
            session_ciphertext=account.session_ciphertext,
            state=account.state.value,
            country_iso=account.country_iso,
            telegram_user_id=account.telegram_user_id,
            telegram_username=account.telegram_username,
            display_name=account.display_name,
            telegram_app_id=account.telegram_app_id,
            telegram_app_hash=account.telegram_app_hash,
            two_factor_secret=account.two_factor_secret,
            reliability_score=account.reliability_score,
            proxy_label=account.proxy_label,
            notes=account.notes,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_account(model)


class SQLAlchemyCampaignRepository(CampaignRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, campaign_id: int) -> Campaign | None:
        model = await self._session.get(CampaignModel, campaign_id)
        return _to_campaign(model) if model else None

    async def list_queued(self, *, limit: int) -> list[Campaign]:
        result = await self._session.execute(
            select(CampaignModel)
            .where(CampaignModel.state == CampaignState.QUEUED.value)
            .order_by(CampaignModel.priority.desc(), CampaignModel.id.asc())
            .limit(limit),
        )
        return [_to_campaign(model) for model in result.scalars()]

    async def create(self, campaign: Campaign) -> Campaign:
        model = CampaignModel(
            engagement_kind=campaign.engagement_kind.value,
            target_count=campaign.target_count,
            fulfilled_count=campaign.fulfilled_count,
            target_spec=campaign.target_spec,
            state=campaign.state.value,
            dedup_fingerprint=campaign.dedup_fingerprint,
            priority=campaign.priority,
            country_filter=campaign.country_filter,
            source_label=campaign.source_label,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_campaign(model)

    async def update_fulfillment(
        self,
        campaign_id: int,
        *,
        fulfilled_count: int,
        state: CampaignState,
    ) -> None:
        model = await self._session.get(CampaignModel, campaign_id)
        if model:
            model.fulfilled_count = fulfilled_count
            model.state = state.value
