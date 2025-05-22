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

# GPT клиент
client = OpenAI(api_key=OPENAI_API_KEY)

# Логи
logging.basicConfig(level=logging.INFO)

# Главное меню
MAIN_MENU = [["📦 Сделать заказ"], ["Отзывы", "Контакты"]]

# Загрузка прайса
def load_prices():
    try:
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"[ERROR] Не удалось загрузить prices.json: {e}")
        return {}

# GPT: извлечение модели
async def extract_model_name(text):
    prompt = f"""
Ты — помощник магазина техники. Клиент написал: "{text}"
Ответь одной строкой — модель и конфигурация (например: iPhone 15 Pro 256GB).
Если не можешь распознать — напиши: ничего не найдено.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # можно заменить на gpt-4, если есть доступ
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        logging.info(f"[GPT]: {result}")
        return result
    except OpenAIError as e:
        logging.error(f"[GPT ERROR]: {e}")
        return f"[GPT ERROR]: {e}"  # ⚠️ Показываем ошибку прямо в Telegram

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Привет! Напиши модель товара или выбери из меню:", reply_markup=keyboard)

# обработка сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logging.info(f"[ПОЛЬЗОВАТЕЛЬ]: {text}")

    prices = load_prices()
    model_string = await extract_model_name(text)

    await update.message.reply_text(f"🤖 GPT распознал: {model_string}")

    if "ошибка" in model_string.lower() or "error" in model_string.lower():
        return  # Ошибка уже показана

    if model_string.lower() in ["ничего не найдено", "непонятно", "не распознал"]:
        await update.message.reply_text("❌ Не удалось распознать товар.")
        return

    for product, configs in prices.items():
        if product.lower() in model_string.lower():
            if isinstance(configs, dict):
                for config_name, price in configs.items():
                    if config_name.lower() in model_string.lower():
                        await update.message.reply_text(f"✅ {product} {config_name}: {price}")
                        return
                await update.message.reply_text(f"{product}:\n" + "\n".join([f"{k}: {v}" for k, v in configs.items()]))
                return
            else:
                await update.message.reply_text(f"{product}: {configs}")
                return

    await update.message.reply_text("❌ Модель не найдена в прайсе.")

# /test команда
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пример: /test айфон 15 про 512")
        return
    text = " ".join(context.args)
    model = await extract_model_name(text)
    await update.message.reply_text(f"GPT понял: {model}")

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_command))  # Тестовое сообщение
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
