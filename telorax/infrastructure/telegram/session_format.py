from __future__ import annotations

import sqlite3
from enum import StrEnum


class SessionLibrary(StrEnum):
    TELETHON = 'telethon'
    PYROGRAM = 'pyrogram'


def detect_session_library(path: str) -> SessionLibrary:
    conn = sqlite3.connect(path, check_same_thread=False)
    try:
        table_names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        }
    finally:
        conn.close()

    telethon_tables = {'sessions', 'entities', 'sent_files', 'update_state', 'version'}
    pyrogram_tables = {'sessions', 'peers', 'version'}

    if telethon_tables.issubset(table_names):
        return SessionLibrary.TELETHON
    if pyrogram_tables.issubset(table_names):
        return SessionLibrary.PYROGRAM

    msg = 'Unsupported or invalid session file'
    raise ValueError(msg)
