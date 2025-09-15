import os
import asyncio
from aiogram import Bot, Dispatcher, types

API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))

CHANNEL_ID = -1002851410256
CHANNEL_NAME = "Київ/обл."

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def main():
    async with bot:
        dp.startup.register(lambda _: print("Бот запущен"))

        @dp.message()
        async def new_link(message: types.Message):
            try:
                invite_link = await bot.create_chat_invite_link(
                    chat_id=CHANNEL_ID,
                    name=f"Ссылка для {CHANNEL_NAME}"
                )
                await bot.send_message(OUTPUT_CHANNEL_ID, f"{CHANNEL_NAME} - {invite_link.invite_link}")
                await message.answer("✅ Ссылка создана и отправлена!")
            except Exception as e:
                await message.answer(f"❌ Ошибка: {e}")

        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
