import os
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))

CHANNELS = {
    -1001111111111: "Київ/обл.",
    -1002222222222: "Харків/обл.",
    -1003333333333: "Одеса/обл.",
    # ... остальные каналы
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["newlinks"])
async def new_links(message: types.Message):
    links = []
    for chat_id, name in CHANNELS.items():
        try:
            invite_link = await bot.create_chat_invite_link(chat_id=chat_id, name=f"Ссылка для {name}")
            links.append(f"{name} - {invite_link.invite_link}")
        except Exception as e:
            links.append(f"{name} - ошибка ({e})")
    # Формируем строки по 3 ссылки
    lines = [" | ".join(links[i:i+3]) for i in range(0, len(links), 3)]
    text = "\n".join(lines)
    await bot.send_message(OUTPUT_CHANNEL_ID, text)
    await message.answer("✅ Ссылки обновлены и отправлены в служебный канал!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
