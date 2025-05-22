import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

# === Загрузка переменных ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Нет ключей в окружении")

openai.api_key = OPENAI_API_KEY

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# Главное меню
MAIN_MENU = [["📦 Сделать заказ"], ["Отзывы", "Контакты"]]

# === Загрузка прайса ===
def load_prices():
    try:
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка чтения prices.json: {e}")
        return {}

# === GPT распознавание модели ===
async def extract_model_name(text):
    prompt = f"""
Ты — помощник магазина. Клиент написал: "{text}"
Ответь одной строкой — модель и конфигурация (например: iPhone 15 Pro 256GB).
Если не уверен, напиши "ничего не найдено".
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        logging.info(f"[GPT]: {result}")
        return result
    except Exception as e:
        logging.error(f"[GPT ERROR]: {e}")
        return "ошибка"

# === Старт ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Привет! Напиши модель, чтобы узнать цену:", reply_markup=keyboard)

# === Основная обработка сообщений ===
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logging.info(f"[USER]: {text}")

    prices = load_prices()
    model_string = await extract_model_name(text)

    await update.message.reply_text(f"🤖 GPT распознал: {model_string}")

    if model_string.lower() in ["ничего не найдено", "ошибка"]:
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

# === Тестовая команда /тест ===
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пример: /тест айфон 15 про 512")
        return
    text = " ".join(context.args)
    model = await extract_model_name(text)
    await update.message.reply_text(f"GPT понял: {model}")

# === Запуск ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("тест", test_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
