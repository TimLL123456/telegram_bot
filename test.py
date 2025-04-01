from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json
import logging

### New Method for Editing Messages

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler
import json
import logging
from dotenv import load_dotenv
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Replace with your web app URL (use HTTPS for production)
WEB_APP_URL = "https://github.com/TimLL123456/telegram_bot"

async def start(update: Update, context):
    # Create a button to open the web app
    keyboard = [
        [InlineKeyboardButton("Edit Transaction", web_app={"url": WEB_APP_URL})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click below to edit a transaction:", reply_markup=reply_markup)

async def handle_web_app_data(update: Update, context):
    # Process data from the web app
    web_app_data = update.message.web_app_data.data
    if web_app_data:
        transaction = json.loads(web_app_data)
        amount = transaction.get("amount")
        category = transaction.get("category")
        date = transaction.get("date")
        # Here, you can save the transaction to a database or process it further
        await update.message.reply_text(
            f"Transaction updated:\n- Amount: ${amount}\n- Category: {category}\n- Date: {date}"
        )
    else:
        await update.message.reply_text("No data received.")

# Custom filter to check for web app data
def web_app_data_filter(update: Update):
    return update.message and update.message.web_app_data is not None

def main():
    # Initialize the bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(web_app_data_filter, handle_web_app_data))
    application.run_polling()

if __name__ == "__main__":
    main()