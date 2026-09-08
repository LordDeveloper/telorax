from __future__ import annotations

from telorax.infrastructure.security.session_cipher import SessionCipher


def test_session_cipher_roundtrip_with_master_key() -> None:
    cipher = SessionCipher('test-master-key')
    encrypted = cipher.encrypt('1ABCDEFsession')
    assert encrypted != '1ABCDEFsession'
    assert cipher.decrypt(encrypted) == '1ABCDEFsession'


def test_session_cipher_plaintext_without_master_key() -> None:
    cipher = SessionCipher(None)
    session = '1ABCDEFsession'
    assert cipher.encrypt(session) == session
    assert cipher.decrypt(session) == session
