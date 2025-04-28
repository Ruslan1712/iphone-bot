import logging
import os
import json
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ========== Настройки ==========
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "@apple_street_41"
MANAGER_CHAT_ID = 658248330  # ID Стеллы
BOT_USERNAME = "Applestreet_41_bot"  # username твоего бота без @

if not TOKEN:
    raise ValueError("❌ Ошибка: переменная окружения TOKEN не установлена.")

# Главное меню
MAIN_MENU = [
    ["iPhone", "Samsung"],
    ["Dyson", "Отзывы"],
    ["📦 Сделать заказ"],
    ["Мы в Telegram", "Наш Instagram"]
]

DYSON_CATEGORIES = [["Стайлеры"], ["Фены"], ["Выпрямители"], ["🔙 Назад"]]
AWAITING_ORDER = {}

# Настройка логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Ключевые слова для автоответчика
PRICE_KEYWORDS = ["цена", "стоимость", "узнать", "сколько стоит", "почем"]
PRODUCT_KEYWORDS = ["iphone", "samsung", "dyson", "айфон", "самсунг", "дайсон", "iphone 15", "iphone 15 pro", "iphone 14", "s24", "s23", "airwrap", "supersonic"]

# ========== Загрузчики данных ==========
def load_prices():
    try:
        with open("prices.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("❌ Файл prices.json не найден.")
        return {}

def load_dyson_stylers():
    try:
        with open("dyson_stylers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("❌ Файл dyson_stylers.json не найден.")
        return {}

# ========== Вспомогательные функции ==========
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

# ========== Основные обработчики ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        keyboard = ReplyKeyboardMarkup([[KeyboardButton("✅ Я подписался")]], resize_keyboard=True)
        await update.message.reply_text("Для использования бота подпишитесь на наш канал: https://t.me/apple_street_41", reply_markup=keyboard)
        return
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Выберите категорию:", reply_markup=keyboard)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not await is_subscribed(user_id, context):
        keyboard = ReplyKeyboardMarkup([[KeyboardButton("✅ Я подписался")]], resize_keyboard=True)
        await update.message.reply_text("Для использования бота подпишитесь на наш канал: https://t.me/apple_street_41", reply_markup=keyboard)
        return

    if user_id in AWAITING_ORDER and AWAITING_ORDER[user_id]:
        await process_order(update, context)
        return

    COMMANDS = {
        "iPhone": handle_iphone,
        "Samsung": handle_samsung,
        "Dyson": handle_dyson,
        "Отзывы": reviews_handler,
        "📦 Сделать заказ": start_order,
        "🔙 Назад": go_back_to_menu,
        "Мы в Telegram": send_telegram_link,
        "Наш Instagram": send_instagram_link,
        "✅ Я подписался": confirm_subscription,
        "Стайлеры": handle_stylers,
    }

    if text in COMMANDS:
        await COMMANDS[text](update, context)
        return

    prices = load_prices()
    if text in prices:
        await send_model_prices(update, context, text)
    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")

async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    text = update.message.text.lower()

    if any(keyword in text for keyword in PRICE_KEYWORDS):
        found_products = [product for product in PRODUCT_KEYWORDS if product in text]

        if found_products:
            product_list = ", ".join(found_products)
            reply_text = f"👋 Хотите узнать цену на *{product_list.title()}*?\nНажмите кнопку ниже 👇"
        else:
            reply_text = "👋 Добрый день! Если хотите узнать стоимость товара, нажмите кнопку ниже 👇"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Узнать цену", url=f"https://t.me/{BOT_USERNAME}?start=price_inquiry")],
            [InlineKeyboardButton("📦 Сделать заказ", url=f"https://t.me/{BOT_USERNAME}?start=order")]
        ])

        try:
            await update.message.reply_text(reply_text, parse_mode="Markdown", reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Ошибка отправки автоответа с кнопками: {e}")

# ========== Функции действий ==========
async def handle_iphone(update, context):
    prices = load_prices()
    iphone_models = [model for model in prices.keys() if model.startswith("iPhone")]
    keyboard = ReplyKeyboardMarkup([[m] for m in iphone_models] + [["🔙 Назад"]], resize_keyboard=True)
    await update.message.reply_text("Выберите модель iPhone:", reply_markup=keyboard)

async def handle_samsung(update, context):
    prices = load_prices()
    samsung_models = [model for model in prices.keys() if model.startswith("Samsung")]
    keyboard = ReplyKeyboardMarkup([[m] for m in samsung_models] + [["🔙 Назад"]], resize_keyboard=True)
    await update.message.reply_text("Выберите модель Samsung:", reply_markup=keyboard)

async def handle_dyson(update, context):
    keyboard = ReplyKeyboardMarkup(DYSON_CATEGORIES, resize_keyboard=True)
    await update.message.reply_text("Выберите категорию Dyson:", reply_markup=keyboard)

async def handle_stylers(update, context):
    dyson_stylers = load_dyson_stylers()
    response = "Прайс на стайлеры Dyson:\n"
    for name, price in dyson_stylers.items():
        response += f"- {name}: {price}\n"
    await update.message.reply_text(response)

async def start_order(update, context):
    user_id = update.effective_user.id
    AWAITING_ORDER[user_id] = True
    await update.message.reply_text("✏️ Пожалуйста, напишите, что вы хотите заказать:")

async def go_back_to_menu(update, context):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Главное меню:", reply_markup=keyboard)

async def send_telegram_link(update, context):
    await update.message.reply_text("Наш Telegram канал: https://t.me/ваш_канал")

async def send_instagram_link(update, context):
    instagram_url = "https://www.instagram.com/apple_street_41?igsh=MXFrYm9rNHFlYzM3Ng=="
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📷 Перейти в Instagram", url=instagram_url)]
    ])
    await update.message.reply_text("📷 Нажмите на кнопку ниже, чтобы перейти в наш Instagram!", reply_markup=keyboard)

async def confirm_subscription(update, context):
    user_id = update.effective_user.id
    if await is_subscribed(user_id, context):
        keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("Спасибо за подписку! Добро пожаловать:", reply_markup=keyboard)
    else:
        await update.message.reply_text("Вы ещё не подписались на канал!")

async def send_model_prices(update, context, model_name):
    prices = load_prices()
    model_info = prices.get(model_name)
    if isinstance(model_info, dict):
        response = f"{model_name}:\n"
        for config, price in model_info.items():
            response += f"- {config}: {price}\n"
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Прайс пуст.")

async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    client_username = update.effective_user.username or "без username"
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    text = update.message.text.strip()

    order_text = (
        "📦 *Новая заявка!*\n\n"
        f"👤 *Клиент:* @{client_username}\n"
        f"🌐 *ID клиента:* `{user_id}`\n"
        f"⏰ *Время заявки:* {now}\n"
        f"📝 *Заказ:* {text}"
    )

    try:
        await context.bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=order_text,
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Ваша заявка принята! Менеджер скоро свяжется с вами.")
    except Exception as e:
        logging.error(f"Ошибка отправки заявки менеджеру: {e}")
        await update.message.reply_text("❌ Ошибка при отправке заявки. Попробуйте позже.")

    AWAITING_ORDER.pop(user_id, None)

async def reviews_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    review_dir = "reviews"
    if not os.path.exists(review_dir):
        await update.message.reply_text("Папка с отзывами не найдена.")
        return

    files = sorted([f for f in os.listdir(review_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
    media = []
    for i, filename in enumerate(files):
        path = os.path.join(review_dir, filename)
        with open(path, "rb") as f:
            caption = "💬 Отзыв клиента" if i == 0 else None
            media.append(InputMediaPhoto(f.read(), caption=caption))
    if media:
        await update.message.reply_media_group(media)
    else:
        await update.message.reply_text("Пока нет отзывов.")

# ========== Запуск приложения ==========
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, message_handler))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, group_message_handler))
    app.run_polling()
