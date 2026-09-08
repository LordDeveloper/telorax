from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


class SessionCipherError(Exception):
    """Raised when session encryption or decryption fails."""


class SessionCipher:
    """Encrypts Telegram session strings at rest using the configured master key."""

    def __init__(self, master_key: str | None) -> None:
        self._fernet = Fernet(self._derive_key(master_key)) if master_key else None

    @staticmethod
    def _derive_key(master_key: str) -> bytes:
        digest = hashlib.sha256(master_key.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def encrypt(self, session_string: str) -> str:
        if self._fernet is None:
            return session_string
        return self._fernet.encrypt(session_string.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if self._fernet is None:
            return ciphertext
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            msg = 'Unable to decrypt stored session'
            raise SessionCipherError(msg) from exc
