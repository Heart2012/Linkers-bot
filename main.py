import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from datetime import datetime, date, timedelta

API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = os.getenv("OUTPUT_CHANNEL_ID")
CHANNEL_ID = -1002851410256  # <- ваш канал
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.onrender.com/webhook/<TOKEN>
STATS_FILE = "stats.json"

if not API_TOKEN or not OUTPUT_CHANNEL_ID or not WEBHOOK_URL:
    print("❌ Ошибка: нет API_TOKEN, OUTPUT_CHANNEL_ID или WEBHOOK_URL")
    exit(1)

OUTPUT_CHANNEL_ID = int(OUTPUT_CHANNEL_ID)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------- Статистика ----------
def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_stats(link_name, link_url, user):
    stats = load_stats()
    stats.append({
        "link_name": link_name,
        "link_url": link_url,
        "user": user,
        "timestamp": datetime.now().isoformat()
    })
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def get_stats_by_day():
    stats = load_stats()
    today = date.today()
    yesterday = today - timedelta(days=1)
    today_count = 0
    yesterday_count = 0
    for item in stats:
        ts = datetime.fromisoformat(item["timestamp"]).date()
        if ts == today:
            today_count += 1
        elif ts == yesterday:
            yesterday_count += 1
    return today_count, yesterday_count

# ---------- Команды ----------
async def handle_commands(message: types.Message):
    text = message.text or ""
    user = message.from_user.username or str(message.from_user.id)

    # Создание новой ссылки
    if text.startswith("/newlink"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("❌ Укажи название ссылки. Пример: /newlink Київ/обл.")
            return
        link_name = parts[1]
        try:
            invite_link = await bot.create_chat_invite_link(chat_id=CHANNEL_ID, name=link_name)
            save_stats(link_name, invite_link.invite_link, user)
            await bot.send_message(OUTPUT_CHANNEL_ID, f"{link_name} - {invite_link.invite_link}")
            await message.answer(f"✅ Ссылка '{link_name}' создана!")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    # Вывод вс
