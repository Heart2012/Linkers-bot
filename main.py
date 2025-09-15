import os
from aiogram import Bot, Dispatcher, executor, types

# Токен бота и ID служебного канала
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))

# ID одного канала
CHANNEL_ID = -1002851410256  # <-- сюда вставь ID своего канала
CHANNEL_NAME = "Київ/обл."   # название канала для отображения

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["newlink"])
async def new_link(message: types.Message):
    try:
        # Создаём ссылку
        invite_link = await bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            name=f"Ссылка для {CHANNEL_NAME}"
        )
        # Отправляем ссылку в служебный канал
        await bot.send_message(OUTPUT_CHANNEL_ID, f"{CHANNEL_NAME} - {invite_link.invite_link}")
        await message.answer("✅ Ссылка создана и отправлена!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)