import os
from aiogram import Bot, Dispatcher, executor, types

# Токен бота и ID служебного канала из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))

# Список каналов
CHANNELS = {
    -1001111111111: "Київ/обл.",
    -1002222222222: "Харків/обл.",
    -1003333333333: "Одеса/обл.",
    -1004444444444: "Дніпро/обл.",
    -1005555555555: "Львів/обл.",
    -1006666666666: "Запоріжжя/обл.",
    -1007777777777: "Кривий Ріг/обл.",
    -1008888888888: "Миколаїв/обл.",
    -1009999999999: "Вінниця/обл.",
    -1001010101010: "Чернігів/обл.",
    -1001111111122: "Полтава/обл.",
    -1001212121212: "Хмельницький/обл.",
    -1001313131313: "Черкаси/обл.",
    -1001414141414: "Чернівці/обл.",
    -1001515151515: "Житомир/обл.",
    -1001616161616: "Суми/обл.",
    -1001717171717: "Рівне/обл.",
    -1001818181818: "Івано-Франківськ/обл.",
    -1001919191919: "Херсон/обл.",
    -1002020202020: "Ужгород/обл.",
    -1002121212121: "Кременчук",
    -1002222222233: "Луцьк/обл.",
    -1002323232323: "Тернопіль/обл.",
    -1002424242424: "Кропивницький/обл.",
    -1002525252525: "⚡️ОПЕРАТИВНІ НОВИНИ УКРАЇНИ 24/7⚡️",
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["newlinks"])
async def new_links(message: types.Message):
    links = []
    for chat_id, name in CHANNELS.items():
        try:
            invite_link = await bot.create_chat_invite_link(
                chat_id=chat_id,
                name=f"Ссылка для {name}"
            )
            links.append(f"{name} - {invite_link.invite_link}")
        except Exception as e:
            links.append(f"{name} - ошибка ({e})")

    # Формируем строки по 3 ссылки в строке
    lines = [" | ".join(links[i:i+3]) for i in range(0, len(links), 3)]
    text = "\n".join(lines)

    await bot.send_message(OUTPUT_CHANNEL_ID, text)
    await message.answer("✅ Ссылки обновлены и отправлены в служебный канал!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)