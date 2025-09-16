import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))
LINKS_FILE = "links.json"

if not API_TOKEN or not OUTPUT_CHANNEL_ID:
    print("❌ Ошибка: не заданы API_TOKEN или OUTPUT_CHANNEL_ID")
    exit(1)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

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

# -------------------- Команды --------------------
@dp.message(Command("newlink"))
async def cmd_newlink(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Укажи название ссылки. Пример: /newlink Київ/обл.")
        return
    link_name = parts[1]

    saved_links = load_links()
    created_links = []

    for ch in CHANNELS:
        try:
            invite = await bot.create_chat_invite_link(chat_id=ch["id"], name=link_name)
            created_links.append({"name": ch["name"], "url": invite.invite_link})
        except Exception as e:
            await message.answer(f"❌ Не удалось создать ссылку для {ch['name']}: {e}")

    # добавляем к старым ссылкам
    all_links = saved_links + created_links
    save_links(all_links)

    # форматируем вывод
    output_lines = [f"{created_links[0]['name']} - {created_links[0]['url']}"]
    for i in range(1, len(created_links), 3):
        group = created_links[i:i+3]
        line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
        output_lines.append(line)

    final_message = "\n".join(output_lines)
    await bot.send_message(OUTPUT_CHANNEL_ID, final_message)
    await message.answer("✅ Все ссылки созданы и опубликованы!")

@dp.message(Command("alllinks"))
async def cmd_alllinks(message: types.Message):
    saved_links = load_links()
    if not saved_links:
        await message.answer("ℹ️ Ссылок пока нет")
        return

    output_lines = [f"{saved_links[0]['name']} - {saved_links[0]['url']}"]
    for i in range(1, len(saved_links), 3):
        group = saved_links[i:i+3]
        line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
        output_lines.append(line)

    await message.answer("\n".join(output_lines))

# -------------------- Запуск --------------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Бот запущен (polling)...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
