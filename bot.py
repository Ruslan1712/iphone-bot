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
    ["\ud83d\udcf1 iPhone", "\ud83d\udcf1 Samsung"],
    ["\ud83d\udca8 Dyson", "\ud83d\udcac \u041e\u0442\u0437\u044b\u0432\u044b"],
    ["\ud83d\udcf2 \u041c\u044b \u0432 Telegram", "\ud83d\udcf8 \u041d\u0430\u0448 Instagram"]
]

DYSON_CATEGORIES = [
    ["\u0421\u0442\u0430\u0439\u043b\u0435\u0440\u044b"],
    ["\u0424\u0435\u043d\u044b"],
    ["\u0412\u044b\u043f\u0440\u044f\u043c\u0438\u0442\u0435\u043b\u0438"],
    ["\ud83d\udd19 \u041d\u0430\u0437\u0430\u0434"]
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
        caption = "\ud83d\udcac \u041e\u0442\u0437\u044b\u0432 \u043a\u043b\u0438\u0435\u043d\u0442\u0430" if i == 0 else None
        media.append(InputMediaPhoto(open(path, "rb"), caption=caption))
    if media:
        await update.message.reply_media_group(media)
    else:
        await update.message.reply_text("\u041f\u043e\u043a\u0430 \u043d\u0435\u0442 \u043e\u0442\u0437\u044b\u0432\u043e\u0432.")

# Стартовое меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c! \u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044e:", reply_markup=keyboard)

# Обработчик сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    prices = load_prices()

    if text == "\ud83d\udcf1 iPhone":
        iphone_models = [model for model in prices.keys() if model.startswith("iPhone")]
        keyboard = ReplyKeyboardMarkup([[m] for m in iphone_models] + [["\ud83d\udd19 \u041d\u0430\u0437\u0430\u0434"]], resize_keyboard=True)
        await update.message.reply_text("\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043c\u043e\u0434\u0435\u043b\u044c iPhone:", reply_markup=keyboard)

    elif text == "\ud83d\udcf1 Samsung":
        samsung_models = [model for model in prices.keys() if model.startswith("Samsung")]
        keyboard = ReplyKeyboardMarkup([[m] for m in samsung_models] + [["\ud83d\udd19 \u041d\u0430\u0437\u0430\u0434"]], resize_keyboard=True)
        await update.message.reply_text("\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043c\u043e\u0434\u0435\u043b\u044c Samsung:", reply_markup=keyboard)

    elif text == "\ud83d\udca8 Dyson":
        keyboard = ReplyKeyboardMarkup(DYSON_CATEGORIES, resize_keyboard=True)
        await update.message.reply_text("\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044e Dyson:", reply_markup=keyboard)

    elif text in prices:
        model_info = prices.get(text)
        if isinstance(model_info, dict):
            response = f"{text}:\n"
            for config, price in model_info.items():
                response += f"- {config}: {price}\n"
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("\u041f\u0440\u0430\u0439\u0441 \u043f\u0443\u0441\u0442.")

    elif text == "\ud83d\udd19 \u041d\u0430\u0437\u0430\u0434":
        keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e:", reply_markup=keyboard)

    elif text == "\ud83d\udcf2 \u041c\u044b \u0432 Telegram":
        await update.message.reply_text("https://t.me/ваш_канал")

    elif text == "\ud83d\udcf8 \u041d\u0430\u0448 Instagram":
        await update.message.reply_text("https://instagram.com/ваш_инстаграм")

    elif text == "\ud83d\udcac \u041e\u0442\u0437\u044b\u0432\u044b":
        await reviews_handler(update, context)

    else:
        await update.message.reply_text("\u041f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0443\u043d\u043a\u0442 \u0438\u0437 \u043c\u0435\u043d\u044e.")

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
