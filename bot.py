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
    "NMN, NAD+, долголетие и антивозрастные добавки",
    "Интервальное голодание и аутофагия",
    "Качество сна, мелатонин и HRV",
    "Солнечный свет, циркадные ритмы и витамин D",
    "Магний, цинк и микроэлементы для здоровья",
    "Микробиом кишечника и пробиотики",
    "Холодный душ, криотерапия и гормезис",
    "Адаптогены: ашваганда, родиола, рейши",
    "Физические упражнения и зоны пульса",
    "Биомаркеры и анализы крови для долголетия",
    "Ресвератрол, куркумин и растительные антиоксиданты",
    "Стресс, кортизол и техники восстановления",
    "Натуропатия и лекарственные растения",
    "Кетоз, метаболизм жиров и когнитивные функции",
]

UNSPLASH_QUERIES = {
    "NMN": "longevity wellness supplements",
    "голодание": "fasting healthy lifestyle",
    "сна": "sleep wellness night",
    "Солнечный": "sunlight nature morning",
    "Магний": "minerals healthy food",
    "Микробиом": "gut health vegetables",
    "Холодный": "cold water ice bath",
    "Адаптогены": "herbs plants natural",
    "упражнения": "fitness workout nature",
    "Биомаркеры": "blood test health",
    "Ресвератрол": "grapes antioxidants berries",
    "Стресс": "meditation calm nature",
    "Натуропатия": "natural herbs medicine",
    "Кетоз": "healthy fats avocado",
}

tema_index = {"i": 0}


def get_next_tema():
    tema = TEME[tema_index["i"] % len(TEME)]
    tema_index["i"] += 1
    return tema


def get_unsplash_query(tema):
    for key, query in UNSPLASH_QUERIES.items():
        if key in tema:
            return query
    return "biohacking health wellness nature"


async def genereaza_postare(tema: str) -> str:
    prompt = f"""Ты эксперт по биохакингу, натуропатии и функциональной медицине.
Напиши короткий практический совет для Telegram-канала на тему: {tema}

Правила:
- Язык: русский
- Длина: 3-4 абзаца, максимум 180 слов
- Начни с сильного хука — первая строка должна захватить внимание
- Используй 2-3 эмодзи, органично вписанных в текст
- Дай 1 конкретный практический совет, который можно применить сегодня
- В конце добавь 4-5 хэштегов: #биохакинг #натуропатия #долголетие и другие релевантные
- Без markdown-форматирования (без звёздочек и подчёркиваний)
- Пиши живо и доступно, как эксперт-друг

Напиши только пост, без объяснений."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 600, "temperature": 0.9},
            },
        )
        data = response.json()
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
    tema = get_next_tema()
    print(f"[{datetime.now()}] Generez postare despre: {tema}")
    try:
        text = await genereaza_postare(tema)
        query = get_unsplash_query(tema)
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
