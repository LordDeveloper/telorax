from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AccountModel(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    msisdn: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    country_iso: Mapped[str | None] = mapped_column(String(3))
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    telegram_username: Mapped[str | None] = mapped_column(String(64))
    display_name: Mapped[str | None] = mapped_column(String(128))
    telegram_app_id: Mapped[int | None] = mapped_column(Integer)
    telegram_app_hash: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[int] = mapped_column(Integer, default=1, index=True)
    session_ciphertext: Mapped[str] = mapped_column(String(1024), nullable=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String(255))
    reliability_score: Mapped[int] = mapped_column(Integer, default=100, index=True)
    rate_limited_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    restricted_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_online_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    two_factor_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    foreign_sessions_revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_engaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    account_ttl_configured: Mapped[bool] = mapped_column(Boolean, default=False)
    proxy_label: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    provisioned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class OperationModel(Base):
    __tablename__ = 'operations'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    operation_type: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[int] = mapped_column(Integer, default=0)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    state: Mapped[int] = mapped_column(Integer, default=2, index=True)
    fingerprint: Mapped[str | None] = mapped_column(String(128), index=True)
    retry_attempts: Mapped[int] = mapped_column(Integer, default=0)
    country: Mapped[str | None] = mapped_column(String(3))
    failure_summary: Mapped[str | None] = mapped_column(Text)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class OperationDispatchModel(Base):
    __tablename__ = 'operation_dispatches'

    operation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    outcome: Mapped[int] = mapped_column(Integer, default=1)
    error_code: Mapped[str | None] = mapped_column(String(64))
    dispatched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class MembershipModel(Base):
    __tablename__ = 'memberships'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(BigInteger, index=True)
    telegram_peer_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    access_hash: Mapped[int | None] = mapped_column(BigInteger)
    peer_kind: Mapped[int] = mapped_column(Integer)
    source_fingerprint: Mapped[str | None] = mapped_column(String(128))
    subscribed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unsubscribe_scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    __table_args__ = (
        Index('ix_membership_account_peer', 'account_id', 'telegram_peer_id'),
    )


class PeerSnapshotModel(Base):
    __tablename__ = 'peer_snapshots'

    telegram_peer_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255), index=True)
    peer_kind: Mapped[int | None] = mapped_column(Integer)
    serialized_peer: Mapped[bytes | None] = mapped_column(Text)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AccountPeerBindingModel(Base):
    __tablename__ = 'account_peer_bindings'

    account_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_peer_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    access_hash: Mapped[int | None] = mapped_column(BigInteger)
    bound_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OperationFailureModel(Base):
    __tablename__ = 'operation_failures'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    operation_id: Mapped[int] = mapped_column(BigInteger, index=True)
    account_id: Mapped[int] = mapped_column(BigInteger, index=True)
    error_message: Mapped[str] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(64))
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
