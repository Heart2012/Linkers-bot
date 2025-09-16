import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ================== Настройки ==================
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))
LINKS_FILE = "links.json"

if not API_TOKEN or not OUTPUT_CHANNEL_ID:
    print("❌ Ошибка: не заданы API_TOKEN или OUTPUT_CHANNEL_ID")
    exit(1)

# ================== Список каналов ==================
CHANNELS = [
    {"name": "⚠️ ОПЕРАТИВНІ НОВИНИ 🔞", "id": -1003039408421},
    {"name": "Київ/обл.", "id": -1002851410256},
    {"name": "Харків/обл.", "id": -1003012571542},
    {"name": "Львів/обл.", "id": -1002969968192},
    {"name": "Вінниця/обл.", "id": -1002924468168},
    {"name": "Дніпро/обл.", "id": -1003021264692},
    {"name": "Запоріжжя/обл.", "id": -1002996278961},
    {"name": "Івано-Франківськ/обл.", "id": -1003006964132},
]

# ================== Работа с JSON ==================
def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_links(links):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

# ================== Создаём бота ==================
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ================== Хендлер команд ==================
@dp.message()
async def handle_commands(message: types.Message):
    text = message.text or ""

    # ---------------- Создание новой ссылки ----------------
    if text.startswith("/newlink"):
        parts = text.split(maxsplit=1)
        link_name = parts[1] if len(parts) > 1 else f"Заявка від {message.from_user.full_name}"

        created_links = []
        for ch in CHANNELS:
            try:
                invite = await bot.create_chat_invite_link(
                    chat_id=ch["id"],
                    name=link_name,
                    creates_join_request=True  # ❗️ закрита лінка з заявкою
                )
                created_links.append({"name": ch["name"], "url": invite.invite_link})
            except Exception as e:
                created_links.append({"name": ch["name"], "url": f"❌ {e}"})

        save_links(created_links)

        # ---------------- Формируем вывод ----------------
        output_lines = []

        if created_links:
            # Первая отдельная
            first_link = created_links[0]
            output_lines.append(f"{first_link['name']} - {first_link['url']}")

            # Все остальные по три в строке через |
            rest_links = created_links[1:]
            for i in range(0, len(rest_links), 3):
                group = rest_links[i:i+3]
                line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
                output_lines.append(line)

        final_message = "\n".join(output_lines)
        await bot.send_message(OUTPUT_CHANNEL_ID, final_message)
        await message.answer("✅ Все ссылки созданы и опубликованы!")

    # ---------------- Показать все ссылки ----------------
    elif text.startswith("/alllinks"):
        saved_links = load_links()
        if not saved_links:
            await message.answer("ℹ️ Лінків ще немає")
            return

        output_lines = []

        if saved_links:
            # Первая отдельная
            first_link = saved_links[0]
            output_lines.append(f"{first_link['name']} - {first_link['url']}")

            # Все остальные по три в строке через |
            rest_links = saved_links[1:]
            for i in range(0, len(rest_links), 3):
                group = rest_links[i:i+3]
                line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
                output_lines.append(line)

        await message.answer("\n".join(output_lines))

# ================== Запуск бота ==================
async def main():
    # Удаляем webhook перед polling
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook удалён, запускаем polling...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
