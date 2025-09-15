import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from datetime import datetime, date, timedelta

API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = os.getenv("OUTPUT_CHANNEL_ID")
CHANNEL_ID = -1002851410256
STATS_FILE = "stats.json"

if not API_TOKEN or not OUTPUT_CHANNEL_ID:
    print("❌ Ошибка: нет API_TOKEN или OUTPUT_CHANNEL_ID")
    exit(1)

OUTPUT_CHANNEL_ID = int(OUTPUT_CHANNEL_ID)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------- СТАТИСТИКА --------------------
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

# -------------------- КОМАНДЫ --------------------
@dp.message()
async def handle_commands(message: types.Message):
    if message.text.startswith("/newlink"):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("❌ Укажи название ссылки.\nПример: /newlink Київ/обл.")
            return

        link_name = parts[1]

        try:
            invite_link = await bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                name=link_name
            )

            save_stats(link_name, invite_link.invite_link, message.from_user.username)

            await bot.send_message(
                OUTPUT_CHANNEL_ID,
                f"{link_name} - {invite_link.invite_link}"
            )
            await message.answer(f"✅ Ссылка '{link_name}' создана!")

        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    elif message.text.startswith("/alllinks"):
        stats = load_stats()
        if not stats:
            await message.answer("ℹ️ Ссылок пока нет")
            return

        links_text = " | ".join(
            [f"{item['link_name']} - {item['link_url']}" for item in stats]
        )
        await message.answer(links_text)

    elif message.text.startswith("/stats"):
        today_count, yesterday_count = get_stats_by_day()
        await message.answer(
            f"📊 Статистика заявок:\n"
            f"Сегодня: {today_count}\n"
            f"Вчера: {yesterday_count}"
        )

# -------------------- WEBHOOK --------------------
async def on_startup(app):
    webhook_path = f"/webhook/{API_TOKEN}"
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{webhook_path}"
    await bot.set_webhook(webhook_url)
    print(f"✅ Webhook установлен: {webhook_url}")

async def on_shutdown(app):
    await bot.delete_webhook()
    print("❌ Webhook удалён")

def main():
    app = web.Application()
    SimpleRequestHandler(dp, bot).register(app, path=f"/webhook/{API_TOKEN}")

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
