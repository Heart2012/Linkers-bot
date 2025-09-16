import os
import json
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ================== Налаштування ==================
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    print("❌ Помилка: не вказано API_TOKEN у Render → Environment")
    exit(1)

# Повний список каналів
CHANNELS = [
    {"name": "Київ/обл.", "id": -1002497921892},
    {"name": "Харків/обл.", "id": -1002282062694},
    {"name": "Одеса/обл.", "id": -1002378112112},
    {"name": "Дніпро/обл.", "id": -1002469953491},
    {"name": "Львів/обл.", "id": -1002462683862},
    {"name": "Запоріжжя/обл.", "id": -1002478382347},
    {"name": "Кривий Ріг", "id": -1002479247381},
    {"name": "Миколаїв/обл.", "id": -1002263502869},
    {"name": "Вінниця/обл.", "id": -1002408714452},
    {"name": "Чернігів/обл.", "id": -1002446393799},
    {"name": "Полтава/обл.", "id": -1002175469997},
    {"name": "Хмельницький/обл.", "id": -1002429587845},
    {"name": "Черкаси/обл.", "id": -1002400669760},
    {"name": "Чернівці/обл.", "id": -1002235399302},
    {"name": "Житомир/обл.", "id": -1002330195140},
    {"name": "Суми/обл.", "id": -1002445729693},
    {"name": "Рівне/обл.", "id": -1002380253993},
    {"name": "Івано-Франківськ/обл.", "id": -1002375309618},
    {"name": "Херсон/обл.", "id": -1002418416457},
    {"name": "Ужгород/обл.", "id": -1002451310310},
    {"name": "Кременчук", "id": -1002261835375},
    {"name": "Луцьк/обл.", "id": -1002293307493},
    {"name": "Тернопіль/обл.", "id": -1002363870955},
    {"name": "Кропивницький/обл.", "id": -1002288269113},
    {"name": "⚡️ОПЕРАТИВНІ НОВИНИ УКРАЇНИ 24/7⚡️", "id": -1002666646029},
]

# Файл для збереження
LINKS_FILE = "links.json"

# Створюємо бота
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# ================== Робота з JSON ==================
def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_links(links):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)


# ================== Хендлери ==================
@dp.message(Command("newlink"))
async def new_link(message: Message):
    """Створює постійні закриті лінки із заявкою"""
    link_name = f"Заявка від {message.from_user.full_name}"

    created_links = []
    for ch in CHANNELS:
        try:
            invite = await bot.create_chat_invite_link(
                chat_id=ch["id"],
                name=link_name,
                creates_join_request=True  # ❗️ постійна закрита заявка
            )
            created_links.append({"name": ch["name"], "url": invite.invite_link})
        except Exception as e:
            created_links.append({"name": ch["name"], "url": f"❌ {e}"})

    save_links(created_links)

    text = "🔗 Постійні закриті лінки із заявкою:\n\n"
    text += "\n".join([f"{item['name']} → {item['url']}" for item in created_links])
    await message.answer(text)


@dp.message(Command("alllinks"))
async def all_links(message: Message):
    """Показує всі збережені лінки"""
    saved = load_links()
    if not saved:
        await message.answer("ℹ️ Лінків ще немає")
        return

    text = "📂 Усі збережені лінки:\n\n"
    text += "\n".join([f"{item['name']} → {item['url']}" for item in saved])
    await message.answer(text)


# ================== Запуск ==================
async def main():
    print("✅ Бот запущено через polling (Render Web Service)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
