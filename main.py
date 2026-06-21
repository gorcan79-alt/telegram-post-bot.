import os
import json
import asyncio
import logging
import re

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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


def build_keyboard(buttons_data):
    rows = []

    for row in buttons_data:
        keyboard_row = []

        for button in row:
            keyboard_row.append(
                InlineKeyboardButton(
                    text=button["text"],
                    url=button["url"]
                )
            )

        rows.append(keyboard_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def publish_post(bot, post):
    keyboard = None

    if "inline_keyboard" in post:
        keyboard = build_keyboard(post["inline_keyboard"])

    # Копирование существующего сообщения
    if "copy_from" in post:
        link = post["copy_from"]

        match = re.search(r"/c/(\d+)/(\d+)", link)

        if not match:
            raise ValueError(f"Неверная ссылка: {link}")

        internal_chat_id = match.group(1)
        message_id = int(match.group(2))

        from_chat_id = int(f"-100{internal_chat_id}")

        await bot.copy_message(
            chat_id=CHANNEL_ID,
            from_chat_id=from_chat_id,
            message_id=message_id
        )

        return

    # Фото с подписью
    if "photo" in post:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=post["photo"],
            caption=post.get("text", ""),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )

        return

    # Обычный текст
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=post.get("text", ""),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=False,
        reply_markup=keyboard
    )


async def main():
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN не найден в переменных окружения"
        )

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

                post_id = (
                    f"{current_date}_{post['time']}"
                )

                if (
                    post["time"] == current_time
                    and post_id not in sent_today
                ):

                    await publish_post(bot, post)

                    sent_today.add(post_id)

                    logging.info(
                        f"Опубликован пост на "
                        f"{post['time']}"
                    )

            if current_time == "00:00":
                sent_today.clear()

            await asyncio.sleep(30)

    except Exception as e:
    logging.exception("Полная ошибка")

            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
```
