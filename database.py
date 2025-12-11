import aiosqlite

DB_NAME = "history.db"

async def init_db() -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS sent_posts
            (
                channel_id TEXT,
                message_id INTEGER,
                sent_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (channel_id, message_id)
            )"""
        )
        await db.commit()

async def is_post_sent(channel_id, message_id) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT 1 FROM sent_posts WHERE channel_id = ? AND message_id = ?",
            (channel_id, message_id)
        )

        return await cursor.fetchone() is not None

async def add_post(channel_id, message_id) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO sent_posts (message_id, channel_id) VALUES (?, ?)",
            (message_id, channel_id)
        )

        await db.commit()