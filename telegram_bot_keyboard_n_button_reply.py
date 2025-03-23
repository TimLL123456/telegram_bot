from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler
)
from dotenv import load_dotenv
import os

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Button 1", callback_data="btn1")],
        [InlineKeyboardButton("Button 2", callback_data="btn2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose button:", reply_markup=reply_markup)

def button_callback(update, context):
    query = update.callback_query
    data = query.data

    if data == "btn1":
        query.answer("You clicked button 1")
    elif data == "btn2":
        query.answer("You clicked button 2")

load_dotenv()
TOKEN = os.getenv("TOKEN")

### Build telegram bot application
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

application.run_polling()