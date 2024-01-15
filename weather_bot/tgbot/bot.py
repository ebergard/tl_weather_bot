import os
import logging
import requests
from enum import Enum
from dotenv import load_dotenv, find_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    filters,
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler
)

load_dotenv(find_dotenv())
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEATHER_URL = "http://127.0.0.1:8000/weather"


class State(Enum):
    WAITING_BTN_PUSH = 1
    WAITING_CITY_NAME = 2


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    keyboard = [
        [InlineKeyboardButton("Узнать погоду", callback_data="Узнать погоду")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Привет! Я знаю всё о погоде в российских городах!",
                                    reply_markup=reply_markup)
    return State.WAITING_BTN_PUSH


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.message.reply_text("Назови город, в котором ты хотел бы узнать погоду:")
    return State.WAITING_CITY_NAME


async def hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    await update.message.reply_text(f"Нажми на кнопку, получишь результат:)")
    return State.WAITING_BTN_PUSH


async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city = update.message.text
    try:
        weather = requests.get(url=WEATHER_URL, params={"city": city}).text
    except Exception:
        weather = "Не могу извлечь данные о погоде"
    await update.message.reply_text(weather)
    await update.message.reply_text(f"До скорых встреч!")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            State.WAITING_BTN_PUSH: [
                CallbackQueryHandler(button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, hint),
            ],
            State.WAITING_CITY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
