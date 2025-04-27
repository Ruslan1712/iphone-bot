import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Вставь сюда свой токен от BotFather
TOKEN = "7470746052:AAGM5VB7rn9-5644HejBbiIYiGwiiQwrsSo"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Главное меню
MAIN_MENU = [
    ["📱 iPhone", "📱 Samsung"],
    ["💨 Dyson", "💬 Отзывы"],
    ["📲 Мы в Telegram", "📸 Наш Instagram"]
]

IPHONE_CATEGORIES = [
    ["iPhone 12"],
    ["iPhone 13"],
    ["iPhone 14"],
    ["iPhone 15"],
    ["iPhone 16"],
    ["🔙 Назад"]
]

SAMSUNG_CATEGORIES = [
    ["Samsung S21"],
    ["Samsung S23"],
    ["Samsung S24"],
    ["Samsung S25"],
    ["🔙 Назад"]
]

DYSON_CATEGORIES = [
    ["Стайлеры"],
    ["Фены"],
    ["Выпрямители"],
    ["🔙 Назад"]
]

# Прайсы (очищены)
PRICES = {
    "iPhone 12": [
        "📱 12 64 green 🇦🇪- — 52000 ₽",
        "📱 12 128 purple 🇦🇪- — 55000 ₽"
    ],
    "iPhone 13": [
        "📱 13 128 midnight 🇦🇪- — 55800 ₽",
        "📱 13 128 green 🇮🇳- — 57000 ₽",
        "📱 13 128 blue 🇮🇳- — 56500 ₽",
        "📱 13 128 starlight 🇮🇳- — 56500 ₽",
        "📱 13 128 red 🇮🇳- — 57000 ₽"
    ],
    "iPhone 14": [
        "📱 14 128 midnight 🇮🇳- — 68000 ₽",
        "📱 14 128 blue 🇮🇳- — 68000 ₽",
        "📱 14 128 purple 🇮🇳- — 68000 ₽",
        "📱 14 128 yellow 🇮🇳- — 64500 ₽",
        "📱 14 plus 128 black 🇪🇺- — 72500 ₽",
        "📱 14 plus 128 blue 🇪🇺- — 72500 ₽",
        "📱 14 plus 128 purple 🇪🇺- — 73500 ₽",
        "📱 14 plus 128 yellow 🇨🇦- — 75000 ₽"
    ],
    "iPhone 15": [
        "📱 15 128 black 🇸🇬- — 72000 ₽",
        "📱 15 128 blue 🇸🇬🇮🇳- — 72000 ₽",
        "📱 15 128 green 🇮🇳- — 72500 ₽",
        "📱 15 128 pink 🇸🇬- — 72000 ₽",
        "📱 15 256 black 🇮🇳- — 81500 ₽",
        "📱 15 256 green 🇮🇳- — 81500 ₽",
        "📱 15 256 pink 🇦🇪- — 81500 ₽",
        "📱 15 plus 128 pink 🇮🇳- — 74500 ₽",
        "📱 15 pro 128 white 🇸🇬- — 94000 ₽",
        "📱 15 pro max 256 blue 🇸🇦- — 109000 ₽",
        "📱 15 pro max 256 natural 🇸🇦- — 109500 ₽",
        "📱 15 pro max 512 blue 🇪🇺🇦🇪- — 116000 ₽",
        "📱 15 pro max 512 white 🇯🇵- — 115500 ₽",
        "📱 15 pro max 1TB natural 🇯🇵- — 119000 ₽"
    ],
    "iPhone 16": [
        "📱 16E 128 Black 🇮🇳- — 64900 ₽",
        "📱 16E 128 White 🇮🇳- — 64600 ₽",
        "📱 16E 256Gb Black 🇮🇳- — 77400 ₽",
        "📱 16E 256Gb White 🇮🇳- — 77400 ₽",
        "📱 16 128 Black 🇮🇳- — 78100 ₽",
        "📱 16 128 White 🇮🇳- — 78700 ₽",
        "📱 16 128 Pink 🇮🇳- — 77400 ₽",
        "📱 16 128 Ultramarine 🇮🇳- — 78100 ₽",
        "📱 16 128 Teal 🇮🇳- — 77900 ₽",
        "📱 16 256 Black 🇮🇳- — 86900 ₽",
        "📱 16 256 White 🇮🇳- — 87900 ₽",
        "📱 16 256 Ultramarine 🇮🇳- — 88900 ₽",
        "📱 16 256 Pink 🇮🇳- — 86700 ₽",
        "📱 16 256 Teal 🇮🇳- — 87400 ₽",
        "📱 16 512 black 🇮🇳- — 110000 ₽",
        "📱 16 Plus 128 Black 🇮🇳- — 87900 ₽",
        "📱 16 Plus 128 Teal 🇮🇳- — 87900 ₽",
        "📱 16 Plus 128 Ultramarine 🇮🇳- — 86900 ₽",
        "📱 16 Plus 128Gb White 🇮🇳- — 87400 ₽",
        "📱 16 Plus 128Gb Pink 🇮🇳- — 88900 ₽",
        "📱 16 Plus 256 Ultramarine 🇮🇳- — 97500 ₽",
        "📱 16 Plus 256 Pink 🇮🇳- — 98000 ₽",
        "📱 16 Plus 256 White 🇮🇳- — 96000 ₽",
        "📱 16 Plus 256 Black 🇮🇳- — 97800 ₽",
        "📱 16 Pro 128 Black 🇯🇵- — 101900 ₽",
        "📱 16 Pro 128 Natural 🇯🇵- — 102200 ₽",
        "📱 16 Pro 128 White 🇯🇵- — 101800 ₽",
        "📱 16 Pro 128 Desert 🇯🇵- — 101900 ₽",
        "📱 16 Pro 256 Natural 🇯🇵- — 114300 ₽",
        "📱 16 Pro 256 White 🇯🇵- — 113000 ₽",
        "📱 16 Pro 256 Black 🇯🇵- — 113300 ₽",
        "📱 16 Pro 256 Desert 🇦🇪- — 112900 ₽",
        "📱 16 Pro 512 Black 🇯🇵- — 128600 ₽",
        "📱 16 Pro 512 White 🇯🇵- — 127400 ₽",
        "📱 16 Pro 1 TB Natural 🇯🇵- — 146500 ₽",
        "📱 16 Pro Max 256 Natural 🇦🇪- — 125000 ₽",
        "📱 16 Pro Max 256 White 🇦🇪- — 121000 ₽",
        "📱 16 Pro Max 256 Desert 🇦🇪- — 121000 ₽",
        "📱 16 Pro Max 512 White 🇯🇵- — 139600 ₽",
        "📱 16 Pro Max 512 Black 🇦🇪- — 141800 ₽",
        "📱 16 Pro Max 512 Desert 🇦🇪- — 140300 ₽",
        "📱 16 Pro Max 512 Natural 🇯🇵- — 141500 ₽",
        "📱 16 Pro Max 1TB Black 🇯🇵- — 150500 ₽",
        "📱 16 Pro Max 1TB White 🇯🇵- — 151500 ₽",
        "📱 16 Pro Max 1TB Natural 🇯🇵- — 149500 ₽",
        "📱 16 Pro Max 1TB Desert 🇯🇵- — 152000 ₽"
    ]
}

# Отзывы — автоматическая загрузка всех фото из папки reviews
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

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Выберите категорию:", reply_markup=keyboard)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📱 iPhone":
        keyboard = ReplyKeyboardMarkup(IPHONE_CATEGORIES, resize_keyboard=True)
        await update.message.reply_text("Выберите модель iPhone:", reply_markup=keyboard)

    elif text == "📱 Samsung":
        keyboard = ReplyKeyboardMarkup(SAMSUNG_CATEGORIES, resize_keyboard=True)
        await update.message.reply_text("Выберите модель Samsung:", reply_markup=keyboard)

    elif text == "💨 Dyson":
        keyboard = ReplyKeyboardMarkup(DYSON_CATEGORIES, resize_keyboard=True)
        await update.message.reply_text("Выберите категорию Dyson:", reply_markup=keyboard)

    elif text in PRICES:
        if PRICES[text]:
            await update.message.reply_text("\n".join(PRICES[text]))
        else:
            await update.message.reply_text("Прайс в данной категории пока пуст.")

    elif text == "🔙 Назад":
        keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("Главное меню:", reply_markup=keyboard)

    elif text == "📲 Мы в Telegram":
        await update.message.reply_text("https://t.me/ваш_канал")

    elif text == "📸 Наш Instagram":
        await update.message.reply_text("https://instagram.com/ваш_инстаграм")

    elif text == "💬 Отзывы":
        await reviews_handler(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")

# Запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_polling()
