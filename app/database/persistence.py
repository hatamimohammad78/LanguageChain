from collections import defaultdict
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from telegram.ext import BasePersistence
from telegram.ext._basepersistence import PersistenceInput


class PostgresPersistence(BasePersistence):
    def __init__(self, database_url: str):
        super().__init__(
            store_data=PersistenceInput(
                user_data=True,
                chat_data=False,
                bot_data=False,
                callback_data=False,
            ),
            update_interval=60,
        )
        if not database_url:
            raise ValueError("DATABASE_URL is required.")

        self.database_url = database_url
        self._initialized = False

    async def initialize(self) -> None:
        async with await psycopg.AsyncConnection.connect(
            self.database_url,
            row_factory=dict_row,
        ) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS languagechain_user_data (
                    user_id BIGINT PRIMARY KEY,
                    data JSONB NOT NULL DEFAULT '{}'::jsonb,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            await conn.commit()

        self._initialized = True

    async def _connect(self):
        if not self._initialized:
            await self.initialize()

        return await psycopg.AsyncConnection.connect(
            self.database_url,
            row_factory=dict_row,
        )

    async def get_user_data(self) -> dict[int, dict]:
        result = defaultdict(dict)

        async with await self._connect() as conn:
            cursor = await conn.execute(
                "SELECT user_id, data FROM languagechain_user_data"
            )
            rows = await cursor.fetchall()

        for row in rows:
            result[int(row["user_id"])] = row["data"] or {}

        return result

    async def update_user_data(self, user_id: int, data: dict) -> None:
        async with await self._connect() as conn:
            await conn.execute(
                """
                INSERT INTO languagechain_user_data (user_id, data, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET
                    data = EXCLUDED.data,
                    updated_at = NOW()
                """,
                (user_id, Jsonb(dict(data))),
            )
            await conn.commit()

    async def refresh_user_data(self, user_id: int, user_data: dict) -> None:
        return

    async def drop_user_data(self, user_id: int) -> None:
        async with await self._connect() as conn:
            await conn.execute(
                "DELETE FROM languagechain_user_data WHERE user_id = %s",
                (user_id,),
            )
            await conn.commit()

    async def get_chat_data(self) -> dict[int, dict]:
        return defaultdict(dict)

    async def update_chat_data(self, chat_id: int, data: dict) -> None:
        return

    async def refresh_chat_data(self, chat_id: int, chat_data: dict) -> None:
        return

    async def drop_chat_data(self, chat_id: int) -> None:
        return

    async def get_bot_data(self) -> dict:
        return {}

    async def update_bot_data(self, data: dict) -> None:
        return

    async def refresh_bot_data(self, bot_data: dict) -> None:
        return

    async def get_conversations(self, name: str) -> dict:
        return {}

    async def update_conversation(
        self,
        name: str,
        key: tuple,
        new_state: Any,
    ) -> None:
        return

    async def get_callback_data(self):
        return None

    async def update_callback_data(self, data) -> None:
        return

    async def flush(self) -> None:
        return
