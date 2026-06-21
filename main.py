import os
import json
import asyncio
import logging
import re

from aiogram import Bot
from datetime import datetime
import pytz

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003860619693

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===== LOAD POSTS =====
def load_posts():
    with open("posts.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ===== COPY MESSAGE PARSER =====
def parse_copy_from(link: str):
    match = re.search(r"/c/(\d+)/(\d+)", link)
    if not match:
        raise ValueError(f"Неверная ссылка copy_from: {link}")

    internal_chat_id = match.group(1)
    message_id = int(match.group(2))

    from_chat_id = int(f"-100{internal_chat_id}")
    return from_chat_id, message_id


# ===== PUBLISH =====
async def publish_post(bot: Bot, post: dict):

    # COPY MODE
    if "copy_from" in post:
        from_chat_id, message_id = parse_copy_from(post["copy_from"])

        await bot.copy_message(
            chat_id=CHANNEL_ID,
            from_chat_id=from_chat_id,
            message_id=message_id
        )
        return

    # TEXT MODE
    if "text" in post:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=post["text"]
        )
        return


# ===== MAIN LOOP =====
async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден")

    bot = Bot(token=BOT_TOKEN)

    moscow = pytz.timezone("Europe/Moscow")

    sent_today = set()

    logging.info("Бот запущен")

    while True:
        try:
            posts = load_posts()

            now = datetime.now(moscow)
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M")

            logging.info(f"Сейчас {current_time}, постов: {len(posts)}")

            for post in posts:

                post_id = f"{current_date}_{post['time']}"

                if post["time"] == current_time and post_id not in sent_today:

                    logging.info(f"Публикую пост {post['time']}")

                    await publish_post(bot, post)

                    sent_today.add(post_id)

                    logging.info(f"Опубликован пост {post['time']}")

            # reset daily
            if current_time == "00:00":
                sent_today.clear()

            await asyncio.sleep(30)

        except Exception:
            logging.exception("Ошибка в основном цикле")
            await asyncio.sleep(60)


# ===== START =====
if __name__ == "__main__":
    asyncio.run(main())
