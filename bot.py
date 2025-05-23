import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI, OpenAIError

# === Загрузка .env ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Нет переменных окружения")

client = OpenAI(api_key=OPENAI_API_KEY)

# Логи
logging.basicConfig(level=logging.INFO)

# Главное меню
MAIN_MENU = [["📦 Сделать заказ"], ["Отзывы", "Контакты"]]
pending_colors = {}  # user_id: base_model

def load_prices():
    try:
        with open("prices_full_ready.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"[ERROR] Не удалось загрузить prices.json: {e}")
        return {}

# GPT обработка
async def extract_model_name(text):
    prompt = f"""
Ты — помощник магазина техники. Клиент написал: "{text}"

Извлеки модель телефона и объём памяти. Пример: "iPhone 16 Pro Max 256".
Если цвет не указан — не придумывай.
Если не можешь распознать — напиши: ничего не найдено.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        logging.info(f"[GPT]: {result}")
        return result
    except OpenAIError as e:
        logging.error(f"[GPT ERROR]: {e}")
        return f"[GPT ERROR]: {e}"

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Привет! Напиши модель телефона (например: Айфон 15 Про Макс 256):", reply_markup=keyboard)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пример: /test айфон 15 про 512")
        return
    text = " ".join(context.args)
    model = await extract_model_name(text)
    await update.message.reply_text(f"GPT понял: {model}")

# Обработка сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    logging.info(f"[ПОЛЬЗОВАТЕЛЬ]: {text}")

    prices = load_prices()

    # Уточнение цвета
    if user_id in pending_colors:
        base_model = pending_colors.pop(user_id)
        for product, configs in prices.items():
            if product.lower() in base_model.lower():
                for config_name, price in configs.items():
                    if base_model.lower() in f"{product} {config_name}".lower() and text.lower() in config_name.lower():
                        await update.message.reply_text(f"✅ {product} {config_name}: {price}")
                        return
        await update.message.reply_text("❌ Указанный цвет не найден.")
        return

    # Основная модель
    model_string = await extract_model_name(text)
    await update.message.reply_text(f"🤖 GPT распознал: {model_string}")

    if "ничего не найдено" in model_string.lower():
        await update.message.reply_text("❌ Не удалось распознать товар.")
        return

    # Поиск по JSON
    for product, configs in prices.items():
        if product.lower() in model_string.lower():
            for config_name, price in configs.items():
                if config_name.lower() in model_string.lower():
                    await update.message.reply_text(f"✅ {product} {config_name}: {price}")
                    return
            # Уточнение цвета
            pending_colors[user_id] = model_string
            await update.message.reply_text("Уточните, пожалуйста, какой цвет вас интересует?")
            return

    await update.message.reply_text("❌ Модель не найдена в прайсе.")

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
