"""Foydalanuvchilar bazasi (SQLite). Faqat rozilik bergan foydalanuvchilar saqlanadi."""
from datetime import datetime, timezone

import aiosqlite

CONSENT_VERSION = "2026-10-v1"  # Rozilik matni o'zgarsa, versiyani yangilang

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id       INTEGER PRIMARY KEY,
    first_name        TEXT,
    last_name         TEXT,
    username          TEXT,
    phone             TEXT,
    email             TEXT,
    marketing_consent INTEGER NOT NULL DEFAULT 0,
    consent_at        TEXT,
    consent_version   TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: str):
        self.path = path

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(SCHEMA)
            await db.commit()

    async def save_consent(self, telegram_id: int, first_name: str | None,
                           last_name: str | None, username: str | None) -> None:
        now = _now()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_id, first_name, last_name, username,
                                   marketing_consent, consent_at, consent_version,
                                   created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    username = excluded.username,
                    marketing_consent = 1,
                    consent_at = excluded.consent_at,
                    consent_version = excluded.consent_version,
                    updated_at = excluded.updated_at
                """,
                (telegram_id, first_name, last_name, username,
                 now, CONSENT_VERSION, now, now),
            )
            await db.commit()

    async def _update(self, telegram_id: int, field: str, value) -> None:
        assert field in {"phone", "email", "marketing_consent"}
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                f"UPDATE users SET {field} = ?, updated_at = ? WHERE telegram_id = ?",
                (value, _now(), telegram_id),
            )
            await db.commit()

    async def set_phone(self, telegram_id: int, phone: str) -> None:
        await self._update(telegram_id, "phone", phone)

    async def set_email(self, telegram_id: int, email: str) -> None:
        await self._update(telegram_id, "email", email)

    async def revoke_consent(self, telegram_id: int) -> None:
        await self._update(telegram_id, "marketing_consent", 0)

    async def delete_user(self, telegram_id: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
            await db.commit()

    async def get_user(self, telegram_id: int) -> dict | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = await cur.fetchone()
            return dict(row) if row else None

    async def consented_ids(self) -> list[int]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT telegram_id FROM users WHERE marketing_consent = 1")
            return [r[0] for r in await cur.fetchall()]

    async def stats(self) -> dict:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """SELECT COUNT(*),
                          SUM(marketing_consent = 1),
                          SUM(phone IS NOT NULL),
                          SUM(email IS NOT NULL)
                   FROM users"""
            )
            total, consented, phones, emails = await cur.fetchone()
            return {"total": total or 0, "consented": consented or 0,
                    "phones": phones or 0, "emails": emails or 0}
