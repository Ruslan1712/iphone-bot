import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Отсутствуют переменные TOKEN или OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Главное меню
MAIN_MENU = [["📦 Сделать заказ"], ["Отзывы", "Контакты"]]

# === Загрузка прайсов ===
def load_prices():
    try:
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки прайса: {e}")
        return {}

# === GPT распознавание товара ===
async def extract_model_name(user_text):
    prompt = f"""
Ты — помощник магазина техники. Клиент написал: "{user_text}"
Извлеки название товара и конфигурацию. Ответь только названием (например: iPhone 15 Pro 256GB).
Если ничего не найдено — напиши: ничего не найдено.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # или gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"GPT ошибка: {e}")
        return "ошибка"

# === Обработка сообщений ===
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    prices = load_prices()

    # GPT пытается распознать товар
    model_string = await extract_model_name(text)
    logging.info(f"Распознано GPT: {model_string}")

    if model_string.lower() in ["ничего не найдено", "ошибка"]:
        await update.message.reply_text("❌ Не удалось распознать товар. Попробуйте написать точнее.")
        return

    # Поиск товара в прайсе
    for product, configs in prices.items():
        if product.lower() in model_string.lower():
            if isinstance(configs, dict):
                for config_name, price in configs.items():
                    if config_name.lower() in model_string.lower():
                        await update.message.reply_text(f"{product} {config_name}: {price}")
                        return
                # Если конфигурация не указана
                lines = [f"{k}: {v}" for k, v in configs.items()]
                await update.message.reply_text(f"{product}:\n" + "\n".join(lines))
            else:
                await update.message.reply_text(f"{product}: {configs}")
            return

    await update.message.reply_text("❌ Модель не найдена в прайсе.")

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Напишите модель, чтобы узнать цену.", reply_markup=keyboard)

# === Запуск бота ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
