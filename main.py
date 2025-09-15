import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))  # канал для публикации всех ссылок
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.onrender.com/webhook/<TOKEN>
LINKS_FILE = "links.json"

if not API_TOKEN or not OUTPUT_CHANNEL_ID or not WEBHOOK_URL:
    print("❌ Ошибка: не заданы API_TOKEN, OUTPUT_CHANNEL_ID или WEBHOOK_URL")
    exit(1)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------- Список всех каналов --------------------
CHANNELS = [
    {"name": "⚠️ ОПЕРАТИВНІ НОВИНИ 🔞", "id": -1003039408421},
    {"name": "Київ/обл.", "id": -1002851410256},
    {"name": "Харків/обл.", "id": -1003012571542},
    {"name": "Львів/обл.", "id": -1002969968192},
    {"name": "Вінниця/обл.", "id": -1002924468168},
    {"name": "Дніпро/обл.", "id": -1003021264692},
    {"name": "Запоріжжя/обл.", "id": -1002996278961},
    {"name": "Івано-Франківськ/обл.", "id": -1003006964132},
    {"name": "Рівне/обл.", "id": -1002945091264},
    {"name": "Хмельницький/обл.", "id": -1002341809057},
    {"name": "Одеса/обл.", "id": -1002628002244},
    {"name": "Чернігів/обл.", "id": -1002966898895},
    {"name": "Луцьк/обл.", "id": -1002946058758},
    {"name": "Тернопіль/обл.", "id": -1003073607738},
    {"name": "Чернівці/обл.", "id": -1002990168271},
    {"name": "Ужгород/обл.", "id": -1002895198278},
    {"name": "Житомир/обл.", "id": -1002915977182},
    {"name": "Черкаси/обл.", "id": -1002320247065},
    {"name": "Миколаїв/обл.", "id": -1003042812683},
    {"name": "Полтава/обл.", "id": -1002792112863},
    {"name": "Суми/обл.", "id": -1002933054536},
    {"name": "Кропивницький/обл.", "id": -1002968550135},
    {"name": "Херсон/обл.", "id": -1003098702380},
    {"name": "Кривий Ріг", "id": -1002816696144},
    {"name": "Кременчук", "id": -1003060893497},
]

# -------------------- Работа с файлами --------------------
def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_links(links):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

# -------------------- Хендлер команд --------------------
async def handle_commands(message: types.Message):
    text = message.text or ""
    user = message.from_user.username or str(message.from_user.id)

    # --- Создание новой ссылки во всех каналах ---
    if text.startswith("/newlink"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("❌ Укажи название ссылки. Пример: /newlink Київ/обл.")
            return
        link_name = parts[1]

        created_links = []
        for ch in CHANNELS:
            try:
                invite = await bot.create_chat_invite_link(chat_id=ch["id"], name=f"{link_name} ({user})")
                created_links.append({"name": ch["name"], "url": invite.invite_link})
            except Exception as e:
                await message.answer(f"❌ Не удалось создать ссылку для {ch['name']}: {e}")

        # Сохраняем все ссылки
        save_links(created_links)

        # Отправляем в OUTPUT_CHANNEL_ID
        for i in range(0, len(created_links), 3):
            group = created_links[i:i+3]
            line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
            await bot.send_message(OUTPUT_CHANNEL_ID, line)

        await message.answer("✅ Все ссылки созданы и опубликованы!")

    # --- Вывод всех ссылок ---
    elif text.startswith("/alllinks"):
        saved_links = load_links()
        if not saved_links:
            await message.answer("ℹ️ Ссылок пока нет")
            return

        lines = []
        first_link = saved_links[0]  # ОПЕРАТИВНІ НОВИНИ
        lines.append(f"{first_link['name']} - {first_link['url']}")

        rest_links = saved_links[1:]
        for i in range(0, len(rest_links), 3):
            group = rest_links[i:i+3]
            line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
            lines.append(line)

        await message.answer("\n".join(lines))

# Регистрируем хендлер
dp.message.register(handle_commands)

# -------------------- Webhook --------------------
async def on_startup(app):
    await bot.delete_webhook(drop_pending_updates=True)
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
