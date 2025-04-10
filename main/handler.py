# Better Code Structure: https://x.com/i/grok/share/qOrvNKRmWUAn4tSFCIJ1I2gHy

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import Database

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = user.id

    print()
    
    greeting_message = (
        "Hello! 👋 <b>Welcome to your Personal Expense Manager Bot</b>. 💰\n\n"
        "I'm here to help you manage your finances easily.\n\n"
        "Click the button below to get started!"
    )
    
    await update.message.reply_text(
        greeting_message,
        parse_mode="HTML"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Operation Menu:\n"
        "- /start: Restart the bot\n"
        "- /menu: Show this menu\n"
        "- More features coming soon!"
    )

def setup_handlers(app):
      app.add_handler(CommandHandler("start", start))
      app.add_handler(CommandHandler("menu", menu))