import logging
import os
import json
from telegram import Update, ReplyKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Токен через переменные окружения
TOKEN = os.getenv("TOKEN")

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Главное меню
MAIN_MENU = [
    ["iPhone", "Samsung"],
    ["Dyson", "Отзывы"],
    ["Мы в Telegram", "Наш Instagram"]
]

DYSON_CATEGORIES = [
    ["Стайлеры"],
    ["Фены"],
    ["Выпрямители"],
    ["🔙 Назад"]
]

# Загрузка прайсов из JSON

def load_prices():
    with open("prices.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Обработчик отзывов

async def reviews_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    review_dir = "reviews"
    files = sorted([f for f in os.listdir(review_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    media = []
    for i, filename in enumerate(files):
        path = os.path.join(review_dir, filename)
        caption = "💬 Отзыв клиента" if i == 0 else None
        media.append(InputMediaPhoto(open(path, "rb"), caption=caption))
    if media:
        await update.message.reply_media_group(media)
    else:
        await update.message.reply_text("Пока нет отзывов.")

# Стартовое меню

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Выберите категорию:", reply_markup=keyboard)

# Обработчик сообщений

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    prices = load_prices()

    if text == "iPhone":
        iphone_models = [model for model in prices.keys() if model.startswith("iPhone")]
        keyboard = ReplyKeyboardMarkup([[m] for m in iphone_models] + [["🔙 Назад"]], resize_keyboard=True)
        await update.message.reply_text("Выберите модель iPhone:", reply_markup=keyboard)

    elif text == "Samsung":
        samsung_models = [model for model in prices.keys() if model.startswith("Samsung")]
        keyboard = ReplyKeyboardMarkup([[m] for m in samsung_models] + [["🔙 Назад"]], resize_keyboard=True)
        await update.message.reply_text("Выберите модель Samsung:", reply_markup=keyboard)

    elif text == "Dyson":
        keyboard = ReplyKeyboardMarkup(DYSON_CATEGORIES, resize_keyboard=True)
        await update.message.reply_text("Выберите категорию Dyson:", reply_markup=keyboard)

    elif text in prices:
        model_info = prices.get(text)
        if isinstance(model_info, dict):
            response = f"{text}:\n"
            for config, price in model_info.items():
                response += f"- {config}: {price}\n"
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Прайс пуст.")

    elif text == "🔙 Назад":
        keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("Главное меню:", reply_markup=keyboard)

    elif text == "Мы в Telegram":
        await update.message.reply_text("https://t.me/ваш_канал")

    elif text == "Наш Instagram":
        await update.message.reply_text("https://instagram.com/ваш_инстаграм")

    elif text == "Отзывы":
        await reviews_handler(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")

# Запуск бота

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
