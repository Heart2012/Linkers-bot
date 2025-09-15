
import os
import asyncio
import json
from aiogram import Bot, Dispatcher, types

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = os.getenv("OUTPUT_CHANNEL_ID")  # служебный канал для ссылок
CHANNEL_ID = -1002851410256  # ID канала, где создаются ссылки

STATS_FILE = "stats.json"  # файл для статистики

# Проверка переменных окружения
if not API_TOKEN or not OUTPUT_CHANNEL_ID:
    print("❌ Ошибка: не заданы переменные окружения API_TOKEN или OUTPUT_CHANNEL_ID")
    exit(1)

OUTPUT_CHANNEL_ID = int(OUTPUT_CHANNEL_ID)

# Создаем бот и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------- Функция для статистики --------------------
def save_stats(link_name, link_url, user):
    stats = []
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats = json.load(f)
    stats.append({
        "link_name": link_name,
        "link_url": link_url,
        "user": user,
        "timestamp": asyncio.get_event_loop().time()
    })
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# -------------------- Удаление webhook перед стартом --------------------
async def remove_webhook():
    await bot.delete_webhook()
    print("Webhook удалён, можно запускать long polling")

# -------------------- Обработчик команды /newlink --------------------
@dp.message()
async def handle_newlink(message: types.Message):
    if message.text.startswith("/newlink"):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer(
                "❌ Укажи название ссылки после команды.\nПример: /newlink Моя ссылка"
            )
            return

        link_name = parts[1]

        try:
            invite_link = await bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                name=link_name
            )

            await bot.send_message(
                OUTPUT_CHANNEL_ID,
                f"{link_name} - {invite_link.invite_link}"
            )
            await message.answer(f"✅ Ссылка '{link_name}' создана и отправлена!")

            # Сохраняем статистику
            save_stats(link_name, invite_link.invite_link, message.from_user.username)
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

# -------------------- Запуск бота --------------------
async def main():
    async with bot:
        await remove_webhook()  # удаляем webhook перед стартом
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
