"""app.py"""
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters
import json

from dotenv import load_dotenv
import os
import logging

import nest_asyncio
nest_asyncio.apply()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
### Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

### Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

async def launch_web_ui(update: Update, callback: CallbackContext):
    # For now, we just display google.com...
    kb = [
        [KeyboardButton("Show me Google!", web_app=WebAppInfo("https://timll123456.github.io/telegram_bot/"))]
    ]
    await update.message.reply_text("Let's do this...", reply_markup=ReplyKeyboardMarkup(kb))


if __name__ == '__main__':
    # when we run the script we want to first create the bot from the token:
    application = ApplicationBuilder().token(TOKEN).build()

    # and let's set a command listener for /start to trigger our Web UI
    application.add_handler(CommandHandler('start', launch_web_ui))

    # and send the bot on its way!
    application.run_polling()
