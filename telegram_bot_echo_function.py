from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

import nest_asyncio
nest_asyncio.apply()

load_dotenv()
TOKEN = os.getenv("TOKEN")

### Build telegram bot application
application = Application.builder().token(TOKEN).build()

async def echo_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

### Add command handler
application.add_handler(CommandHandler("hello", echo_))

application.run_polling()