import asyncio
import logging
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait

import config
import database

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Client(config.SESSION_NAME, api_id=config.API_ID, api_hash=config.API_HASH)


def calculate_score(message) -> int:
    views = message.views or 0
    reaction_count = 0

    if message.reactions:
        for _ in message.reactions.reactions:
            reaction_count += 1

    score = views + (reaction_count * config.REACTION_MULTIPLIER)
    return score


async def job():
    logger.info("Starting job")

    now = datetime.now()
    search_limit = now - timedelta(hours=config.SEARCH_WINDOW_HOURS)
    cooldown_limit = now - timedelta(hours=config.COOLDOWN_HOURS)

    candidates = []

    media_groups = {}

    async with app:
        await database.init_db()

        async for message in app.get_chat_history(config.SOURCE_CHANNEL_ID, limit=200):
            if message.date < search_limit:
                break

            if message.date > cooldown_limit:
                continue

            if message.service:
                continue

            if await database.is_post_sent(config.SOURCE_CHANNEL_ID, message.id):
                continue

            if message.media_group_id:
                if message.media_group_id not in media_groups:
                    media_groups[message.media_group_id] = []
                media_groups[message.media_group_id].append(message)
                continue

            candidates.append({"msg": message, "score": calculate_score(message), "is_album": False, })

        for mg_id, messages in media_groups.items():
            already_sent = False

            for part in messages:
                if await database.is_post_sent(config.SOURCE_CHANNEL_ID, part.id):
                    already_sent = True
                    break

            if already_sent:
                continue

            representative = messages[0]

            candidates.append({"msg": representative, "score": calculate_score(representative), "is_album": True,
                               "album_messages": messages, })

        if not candidates:
            logger.info("No candidate messages found")
            return

        best_post = max(candidates, key=lambda x: x["score"])

        logger.info("Best post found: ID {}, Score {}".format(best_post["msg"].id, best_post["score"]))

        try:
            target = config.TARGET_CHANNEL_ID
            source = config.SOURCE_CHANNEL_ID

            caption = f"Больше контента в <a href='{config.PROMO_CHANNEL_URL}'>{config.PROMO_CHANNEL_NAME}</a>"

            if best_post["is_album"]:
                await app.copy_media_group(chat_id=target, from_chat_id=source, message_id=best_post["msg"].id,
                                           captions=caption)

                for part in best_post["album_messages"]:
                    await database.add_post(source, part.id)

            else:
                await app.copy_message(chat_id=target, from_chat_id=source, message_id=best_post["msg"].id,
                                       caption=caption, parse_mode=ParseMode.HTML)

                await database.add_post(source, best_post["msg"].id)

            logger.info("Post sent")

        except FloodWait as e:
            logger.warning("Flood wait, sleeping for {}".format(e.value))
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error("Error while sending message: {}".format(e))


async def scheduler():
    logger.info("Starting scheduler")

    while True:
        now = datetime.now()
        next_run = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        sleep_seconds = (next_run - now).total_seconds()

        logger.info("Next run: on {} in {:.0f}".format(next_run, sleep_seconds))

        await asyncio.sleep(sleep_seconds)

        await asyncio.sleep(1)
        await job()


if __name__ == "__main__":
    app.run(scheduler())
