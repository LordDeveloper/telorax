from __future__ import annotations

import asyncio
import json
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.tl import functions

from telorax.core.exceptions import AccountImportError, InvalidSessionError
from telorax.infrastructure.telegram.fluxsession import SessionManager
from telorax.infrastructure.telegram.session_format import SessionLibrary, detect_session_library

if TYPE_CHECKING:
    from telorax.core.config.settings import Settings


@dataclass(frozen=True, slots=True)
class SessionImportOptions:
    password: str | None = None
    ignore_revoke: bool = False
    ignore_2fa: bool = False
    renew: bool = True


@dataclass(frozen=True, slots=True)
class SessionImportResult:
    msisdn: int
    telegram_user_id: int
    telegram_username: str | None
    display_name: str | None
    country_iso: str | None
    session_string: str
    telegram_app_id: int
    telegram_app_hash: str
    two_factor_secret: str | None
    ignore_revoke: bool
    ignore_2fa: bool


class SessionImporter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def import_file(self, content: bytes, options: SessionImportOptions) -> SessionImportResult:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            return await self._import_from_path(temp_file.name, options)

    async def _import_from_path(self, path: str, options: SessionImportOptions) -> SessionImportResult:
        try:
            library = detect_session_library(path)
        except ValueError as exc:
            raise InvalidSessionError(str(exc)) from exc

        try:
            if library is SessionLibrary.TELETHON:
                manager = SessionManager.from_telethon_file(path)
            else:
                manager = SessionManager.from_pyrogram_session_file(path)
            session_string = manager.telethon_string_session()
        except ValueError as exc:
            raise InvalidSessionError(str(exc)) from exc

        app = self._pick_telegram_app()
        imported_client, renewed_client = self._build_clients(session_string, app, options.renew)
        active_client = renewed_client if options.renew else imported_client

        try:
            await asyncio.gather(imported_client.connect(), renewed_client.connect())
            if options.renew:
                await self._renew_session(imported_client, renewed_client, options.password)
            me = await active_client.get_me()
            if me.phone is None:
                msg = 'Imported session has no phone number'
                raise AccountImportError(msg)
            session_string = active_client.session.save()
        except InvalidSessionError:
            raise
        except Exception as exc:
            msg = f'Session import failed: {exc}'
            raise AccountImportError(msg) from exc
        finally:
            await asyncio.gather(
                self._safe_disconnect(imported_client),
                self._safe_disconnect(renewed_client),
                return_exceptions=True,
            )

        country_iso = self._resolve_country_iso(me.phone)
        display_name = ' '.join(part for part in (me.first_name, me.last_name) if part) or None
        return SessionImportResult(
            msisdn=int(me.phone),
            telegram_user_id=me.id,
            telegram_username=me.username,
            display_name=display_name,
            country_iso=country_iso,
            session_string=session_string,
            telegram_app_id=app['api_id'],
            telegram_app_hash=app['api_hash'],
            two_factor_secret=options.password,
            ignore_revoke=options.ignore_revoke,
            ignore_2fa=options.ignore_2fa,
        )

    def _pick_telegram_app(self) -> dict[str, int | str]:
        apps_file = self._settings.telegram_apps_file
        if apps_file and Path(apps_file).is_file():
            apps = json.loads(Path(apps_file).read_text(encoding='utf-8'))
            if apps:
                return random.choice(apps)

        api_id = self._settings.telegram_default_api_id
        api_hash = self._settings.telegram_default_api_hash
        if not api_id or not api_hash:
            msg = 'Telegram API credentials are not configured'
            raise AccountImportError(msg)
        return {'api_id': api_id, 'api_hash': api_hash}

    def _build_clients(
        self,
        session_string: str,
        app: dict[str, int | str],
        renew: bool,
    ) -> tuple[TelegramClient, TelegramClient]:
        api_id = int(app['api_id'])
        api_hash = str(app['api_hash'])
        imported = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash,
            connection_retries=self._settings.telegram_connection_retries,
            request_retries=self._settings.telegram_request_retries,
            timeout=self._settings.telegram_connection_timeout,
        )
        renewed = TelegramClient(
            StringSession(),
            api_id,
            api_hash,
            connection_retries=self._settings.telegram_connection_retries,
            request_retries=self._settings.telegram_request_retries,
            timeout=self._settings.telegram_connection_timeout,
        )
        proxy = self._resolve_proxy(use_proxy=renew)
        if proxy is not None:
            imported.set_proxy(proxy)
            renewed.set_proxy(proxy)
        return imported, renewed

    def _resolve_proxy(self, *, use_proxy: bool) -> tuple | dict | None:
        if not self._settings.proxy_url:
            return None
        if not use_proxy and not self._settings.proxy_use_global:
            return None
        import socks

        parsed = urlparse(self._settings.proxy_url)
        proxy_types = {
            'http': socks.PROXY_TYPE_HTTP,
            'socks4': socks.PROXY_TYPE_SOCKS4,
            'socks5': socks.PROXY_TYPE_SOCKS5,
        }
        proxy_type = proxy_types.get(parsed.scheme)
        if proxy_type is None:
            return None
        return (
            proxy_type,
            parsed.hostname,
            parsed.port,
            True,
            parsed.username,
            parsed.password,
        )

    async def _renew_session(
        self,
        imported_client: TelegramClient,
        renewed_client: TelegramClient,
        password: str | None,
    ) -> None:
        qr = await renewed_client.qr_login()

        async def wait_for_qr() -> None:
            try:
                await qr.wait()
            except SessionPasswordNeededError:
                if not password:
                    msg = 'Two-factor password is required for this session'
                    raise AccountImportError(msg)
                await renewed_client.sign_in(password=password)

        await asyncio.gather(
            wait_for_qr(),
            imported_client(functions.auth.AcceptLoginTokenRequest(token=qr.token)),
        )

    @staticmethod
    async def _safe_disconnect(client: TelegramClient) -> None:
        if client.is_connected():
            await client.disconnect()

    @staticmethod
    def _resolve_country_iso(phone: str) -> str | None:
        try:
            import phonenumbers
        except ImportError:
            return None
        try:
            return phonenumbers.region_code_for_number(phonenumbers.parse(f'+{phone}'))
        except phonenumbers.NumberParseException:
            return None
