from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
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

async def greet_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(f"Hi {user.mention_html()}!", parse_mode="HTML")

async def echo_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"You said: {update.message.text}", parse_mode="HTML")

def main():

    ### Build telegram bot application
    application = Application.builder().token(TOKEN).build()

    ### Add command: /start - echo the message
    application.add_handler(CommandHandler("start", greet_user))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_))

    ### Start the bot
    print("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()