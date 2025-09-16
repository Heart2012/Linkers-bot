import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))
LINKS_FILE = "links.json"
OUTPUT_CHANNEL_ID = os.getenv("OUTPUT_CHANNEL_ID")
ADMINS = [int(os.getenv("ADMIN_ID", 0))]  # ID админов через переменные окружения

if not API_TOKEN or not OUTPUT_CHANNEL_ID:
if not API_TOKEN or OUTPUT_CHANNEL_ID is None:
    print("❌ Ошибка: не заданы API_TOKEN или OUTPUT_CHANNEL_ID")
    exit(1)

OUTPUT_CHANNEL_ID = int(OUTPUT_CHANNEL_ID)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # aiogram 3.x
dp = Dispatcher()

LINKS_FILE = "links.json"

# -------------------- Список каналов --------------------
CHANNELS = [
@@ -58,6 +62,9 @@
# -------------------- Хендлер команд --------------------
@dp.message()
async def handle_commands(message: types.Message):
    if message.from_user.id not in ADMINS:
        return  # Только админы могут использовать бота

    text = message.text or ""

    # ---------------- Создание новой ссылки ----------------
@@ -78,30 +85,16 @@

        save_links(created_links)

        # ---------------- Формируем вывод ----------------
        # ---------------- Формируем текст одним сообщением ----------------
        # ---------------- Формируем текст для вывода ----------------
        output_lines = []

        # Первая ссылка отдельно
        first_link = created_links[0]
        output_lines.append(f"{first_link['name']} - {first_link['url']}")

        # Остальные по 3 в строке
        rest_links = created_links[1:]
        for i in range(0, len(rest_links), 3):
            group = rest_links[i:i+3]
        for i in range(0, len(created_links), 3):
            group = created_links[i:i+3]
            line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
            output_lines.append(line)

        # Отправляем в OUTPUT_CHANNEL_ID
        for line in output_lines:
            await bot.send_message(OUTPUT_CHANNEL_ID, line)
        # Всё одной строкой через переносы
        final_message = "\n".join(output_lines)

        # Отправляем в OUTPUT_CHANNEL_ID одним сообщением
        await bot.send_message(OUTPUT_CHANNEL_ID, final_message)

        await message.answer("✅ Все ссылки созданы и опубликованы!")

    # ---------------- Показать все ссылки ----------------
@@ -112,20 +105,15 @@
            return

        output_lines = []
        first_link = saved_links[0]
        output_lines.append(f"{first_link['name']} - {first_link['url']}")

        rest_links = saved_links[1:]
        for i in range(0, len(rest_links), 3):
            group = rest_links[i:i+3]
        for i in range(0, len(saved_links), 3):
            group = saved_links[i:i+3]
            line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
            output_lines.append(line)

        await message.answer("\n".join(output_lines))

# -------------------- Запуск бота --------------------
async def main():
    # Удаляем webhook перед polling
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook удалён, запускаем polling...")
