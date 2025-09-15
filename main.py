import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from datetime import datetime, date, timedelta

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")  # токен бота
OUTPUT_CHANNEL_ID = os.getenv("OUTPUT_CHANNEL_ID")  # канал для публикации ссылок
CHANNEL_ID = -1002851410256  # канал, где создаются ссылки
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.onrender.com/webhook/<TOKEN>
STATS_FILE = "stats.json"

if not API_TOKEN or not OUTPUT_CHANNEL_ID or not WEBHOOK_URL:
    print("❌ Ошибка: не заданы API_TOKEN, OUTPUT_CHANNEL_ID или WEBHOOK_URL")
    exit(1)

OUTPUT_CHANNEL_ID = int(OUTPUT_CHANNEL_ID)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------- Статистика --------------------
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

# -------------------- Хендлер команд --------------------
async def handle_commands(message: types.Message):
    text = message.text or ""
    user = message.from_user.username or str(message.from_user.id)

    # --- Создание новой ссылки ---
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

    # --- Вывод всех ссылок по 3 в строке ---
    elif text.startswith("/alllinks"):
        stats = load_stats()
        if not stats:
            await message.answer("ℹ️ Ссылок пока нет")
            return
        lines = []
        for i in range(0, len(stats), 3):
            group = stats[i:i+3]
            line = " | ".join([f"{item['link_name']} - {item['link_url']}" for item in group])
            lines.append(line)
        await message.answer("\n".join(lines))

    # --- Статистика заявок ---
    elif text.startswith("/stats"):
        today_count, yesterday_count = get_stats_by_day()
        await message.answer(
            f"📊 Статистика заявок:\n"
            f"Сегодня: {today_count}\n"
            f"Вчера: {yesterday_count}"
        )

# Регистрируем хендлер (aiogram v3)
dp.message.register(handle_commands)

# -------------------- Webhook --------------------
async def on_startup(app):
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook удалён и pending updates очищены")
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    print("❌ Webhook удалён")

# -------------------- Запуск веб-сервера --------------------
def main():
    app = web.Application()
    SimpleRequestHandler(dp, bot).register(app, path=f"/webhook/{API_TOKEN}")

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
