import os
import asyncio
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
UNSPLASH_ACCESS_KEY = os.environ["UNSPLASH_ACCESS_KEY"]
TIMEZONE = os.environ.get("TIMEZONE", "Europe/Bucharest")

TEME = [
    ("лайфхак", "Полезные лайфхаки для здоровья и долголетия"),
    ("природа", "Природные средства и рецепты для здоровья"),
    ("природа", "Народные рецепты и натуральные средства от распространённых недугов"),
    ("лайфхак", "Простые привычки для улучшения самочувствия каждый день"),
    ("советы", "Советы по исцелению и поддержанию здоровья"),
    ("советы", "Как укрепить иммунитет естественными методами"),
    ("новости", "Новости в мире здоровья и натуропатии"),
    ("природа", "Лекарственные растения и их применение в быту"),
    ("лайфхак", "Биохакинг для начинающих — простые шаги к здоровью"),
    ("советы", "Детокс и очищение организма природными методами"),
    ("новости", "Последние исследования о натуральном питании и здоровье"),
    ("природа", "Эфирные масла и ароматерапия для здоровья"),
    ("лайфхак", "Утренние ритуалы для энергии и бодрости"),
    ("советы", "Сон и восстановление — советы по улучшению качества сна"),
    ("природа", "Суперфуды и натуральные добавки для здоровья"),
    ("новости", "Тренды здорового образа жизни и натуропатии"),
]

UNSPLASH_QUERIES = {
    "лайфхак": "healthy lifestyle wellness tips",
    "природа": "natural herbs plants medicine",
    "советы": "health wellness healing nature",
    "новости": "health science research nature",
}

tema_index = {"i": 0}


def get_next_tema():
    tema_tuple = TEME[tema_index["i"] % len(TEME)]
    tema_index["i"] += 1
    return tema_tuple


def get_unsplash_query(tema_tuple):
    tip, _ = tema_tuple
    return UNSPLASH_QUERIES.get(tip, "natural health wellness nature")


async def genereaza_postare(tema_tuple: tuple) -> str:
    tip, tema = tema_tuple

    tip_formatat = {
        "лайфхак": "🔸 Полезные лайфхаки",
        "природа": "🔹 Природные средства и рецепты",
        "советы": "🔸 Советы по исцелению и поддержанию здоровья",
        "новости": "🔹 Новости в мире здоровья",
    }.get(tip, "🔸 Здоровье")

    prompt = f"""Ты эксперт по натуропатии, народной медицине и здоровому образу жизни.
Напиши пост для Telegram-канала в рубрике "{tip_formatat}" на тему: {tema}

Правила:
- Язык: русский
- Начни пост с эмодзи и названия рубрики: {tip_formatat}
- Длина: 3-4 абзаца, максимум 200 слов
- Первая строка после рубрики должна захватить внимание
- Используй 2-3 эмодзи органично в тексте
- Дай 1-2 конкретных практических совета
- В конце добавь 4-5 хэштегов: #здоровье #натуропатия #народнаямедицина и другие релевантные
- Без markdown-форматирования (без звёздочек и подчёркиваний)
- Пиши тепло и доступно, как мудрый друг

Напиши только пост, без объяснений."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview:generateContent?key={GEMINI_API_KEY}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 600, "temperature": 0.9},
            },
        )
        data = response.json()
        print(f"Gemini response: {data}")
        if "candidates" not in data:
            raise Exception(f"Gemini error: {data}")
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def get_unsplash_image(query: str) -> str | None:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://api.unsplash.com/photos/random",
            params={
                "query": query,
                "orientation": "landscape",
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
        )
        if response.status_code == 200:
            data = response.json()
            return data["urls"]["regular"]
    return None


async def send_to_telegram(text: str, image_url: str | None):
    async with httpx.AsyncClient(timeout=30) as client:
        if image_url:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                json={
                    "chat_id": TELEGRAM_CHANNEL,
                    "photo": image_url,
                    "caption": text,
                    "parse_mode": "HTML",
                },
            )
        else:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHANNEL,
                    "text": text,
                    "parse_mode": "HTML",
                },
            )


async def posteaza():
    tema_tuple = get_next_tema()
    _, tema_text = tema_tuple
    print(f"[{datetime.now()}] Generez postare despre: {tema_text}")
    try:
        text = await genereaza_postare(tema_tuple)
        query = get_unsplash_query(tema_tuple)
        image_url = await get_unsplash_image(query)
        await send_to_telegram(text, image_url)
        print(f"[{datetime.now()}] Postat cu succes! Imagine: {'da' if image_url else 'nu'}")
    except Exception as e:
        print(f"[{datetime.now()}] Eroare: {e}")


async def main():
    tz = pytz.timezone(TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=tz)

    scheduler.add_job(posteaza, "cron", hour=9, minute=0)
    scheduler.add_job(posteaza, "cron", hour=19, minute=0)

    scheduler.start()
    print(f"Bot pornit! Postare la 09:00 si 19:00 ({TIMEZONE})")

    await posteaza()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
