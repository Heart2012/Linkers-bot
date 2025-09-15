import os
import asyncio
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")  # токен бота
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))  # куда присылать ссылки
SERVICE_ACCOUNT_FILE = "service_account.json"  # JSON ключ Google
SHEET_NAME = "TelegramBotStats"  # имя Google таблицы

# Список каналов (ID: название для сообщения)
CHANNELS = {
    -1003039408421: "Київ/обл.",
    -1002851410256: "Харків/обл.",
    -1003012571542: "Львів/обл.",
    -1002969968192: "Вінниця/обл.",
    -1002924468168: "Дніпро/обл.",
    -1003021264692: "Запоріжжя/обл.",
    -1002996278961: "Івано-Франківськ/обл.",
    -1003006964132: "Рівне/обл.",
    -1002945091264: "Хмельницький/обл.",
    -1002341809057: "Одеса/обл.",
    -1002628002244: "Чернігів/обл.",
    -1002966898895: "Луцьк/обл."
    # Добавьте остальные каналы
}

# -------------------- Инициализация бота --------------------
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------- Google Sheets --------------------
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1  # используем первый лист

def log_to_sheet(link_name, channel_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, link_name, channel_name])

def generate_daily_report():
    records = sheet.get_all_records()
    today = date.today()
    yesterday = today - timedelta(days=1)
    report = {"today": {}, "yesterday": {}}

    for r in records:
        ts = datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S").date()
        channel = r["channel_name"]
        if ts == today:
            report["today"][channel] = report["today"].get(channel, 0) + 1
        elif ts == yesterday:
            report["yesterday"][channel] = report["yesterday"].get(channel, 0) + 1
    return report

# -------------------- Команда /newlink --------------------
@dp.message(commands=["newlink"])
async def cmd_newlink(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❌ Укажи название ссылки. Пример: /newlink Моя ссылка")
        return
    link_name = parts[1]

    links_text_list = []
    for channel_id, name in CHANNELS.items():
        try:
            invite_link = await bot.create_chat_invite_link(chat_id=channel_id, name=link_name)
            links_text_list.append(f"{name} - {invite_link.invite_link}")
            log_to_sheet(link_name, name)
        except Exception as e:
            links_text_list.append(f"{name} - ❌ ошибка: {e}")

    # Формируем сообщение по 3 ссылки в ряд
    message_lines = []
    for i in range(0, len(links_text_list), 3):
        message_lines.append(" | ".join(links_text_list[i:i+3]))
    final_message = "\n".join(message_lines)

    await bot.send_message(OUTPUT_CHANNEL_ID, final_message, parse_mode=ParseMode.HTML)
    await message.reply("✅ Ссылки созданы и отправлены!")

# -------------------- Команда /report --------------------
@dp.message(commands=["report"])
async def cmd_report(message: types.Message):
    report = generate_daily_report()
    text = "📊 Статистика по ссылкам:\n\nСегодня:\n"
    for ch, count in report["today"].items():
        text += f"{ch}: {count}\n"
    text += "\nВчера:\n"
    for ch, count in report["yesterday"].items():
        text += f"{ch}: {count}\n"
    await message.reply(text)

# -------------------- Запуск --------------------
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
