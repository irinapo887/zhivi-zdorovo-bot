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
TIMEZONE = os.environ.get("TIMEZONE", "Europe/Brussels")

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

    prompt = f"""Напиши короткий Telegram-пост на русском языке. Тема: {tema}.

Пост должен содержать ровно 4 части:
1. Заголовок: {tip_formatat}
2. Один абзац (3-4 предложения) с полезной информацией по теме
3. Один конкретный совет что сделать сегодня (1-2 предложения с эмодзи)
4. Хэштеги: #здоровье #натуропатия #народнаямедицина #ЖивиЗдорово #здоровыйобразжизни

Общая длина: не более 100 слов. Без markdown."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 256, "temperature": 0.8},
            },
        )
        data = response.json()
        if "candidates" not in data:
            raise Exception(f"Gemini error: {data}")
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        if "#здоровье" not in text:
            text += "\n\n#здоровье #натуропатия #народнаямедицина #ЖивиЗдорово #здоровыйобразжизни"
        return text


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
                },
            )
        resp = await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHANNEL,
                "text": text,
            },
        )
        print(f"Telegram response: {resp.json()}")


async def posteaza():
    tema_tuple = get_next_tema()
    _, tema_text = tema_tuple
    print(f"[{datetime.now()}] Generez postare despre: {tema_text}")
    try:
        text = await genereaza_postare(tema_tuple)
        query = get_unsplash_query(tema_tuple)
        image_url = await get_unsplash_image(query)
        await send_to_telegram(text, image_url)
        print(f"[{datetime.now()}] Postat cu succes!")
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
