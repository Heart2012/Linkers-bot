import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))
LINKS_FILE = "links.json"

if not API_TOKEN or not OUTPUT_CHANNEL_ID:
    print("❌ Ошибка: не заданы API_TOKEN или OUTPUT_CHANNEL_ID")
    exit(1)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # aiogram 3.x

# -------------------- Список каналов --------------------
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

# -------------------- Работа с JSON --------------------
def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_links(links):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

# -------------------- Хендлер команд --------------------
@dp.message()
async def handle_commands(message: types.Message):
    text = message.text or ""

    # ---------------- Создание новой ссылки ----------------
    if text.startswith("/newlink"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
@@ -77,7 +78,7 @@

        save_links(created_links)

        # -------------------- Формируем вывод --------------------
        # ---------------- Формируем вывод ----------------
        output_lines = []

        # Первая ссылка отдельно
@@ -97,6 +98,7 @@

        await message.answer("✅ Все ссылки созданы и опубликованы!")

    # ---------------- Показать все ссылки ----------------
    elif text.startswith("/alllinks"):
        saved_links = load_links()
        if not saved_links:
@@ -117,12 +119,12 @@

# -------------------- Запуск бота --------------------
async def main():
    # Удаляем webhook, чтобы не было конфликта
    # Удаляем webhook перед polling
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook удалён, запускаем polling...")

    try:
        await dp.start_polling()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
