import os
import json
import asyncio
import logging

from aiogram import Bot
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_ID = -1003860619693

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_posts():
    with open("posts.json", "r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")

    bot = Bot(token=BOT_TOKEN)

    moscow_tz = pytz.timezone("Europe/Moscow")

    sent_today = set()

    logging.info("Бот запущен")

    while True:
        try:
            posts = load_posts()

            now = datetime.now(moscow_tz)

            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M")

            for post in posts:
                post_id = f"{current_date}_{post['time']}"

                if (
                    post["time"] == current_time
                    and post_id not in sent_today
                ):

                    if "message_id" in post:
                        await bot.copy_message(
                            chat_id=CHANNEL_ID,
                            from_chat_id=post["source_chat_id"],
                            message_id=post["message_id"]
                        )
                    else:
                        await bot.send_message(
                            chat_id=CHANNEL_ID,
                            text=post["text"]
                        )

                    sent_today.add(post_id)

                    logging.info(
                        f"Опубликован пост на {post['time']}"
                    )

            if current_time == "00:00":
                sent_today.clear()

            await asyncio.sleep(30)

        except Exception as e:
            logging.exception("Ошибка")
            await asyncio.sleep(60)


    if __name__ == "__main__":
        asyncio.run(main())
