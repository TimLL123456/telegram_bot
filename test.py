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

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create an inline keyboard with a button
    keyboard = [
        [
            InlineKeyboardButton(
                "Search Inline Here",
                switch_inline_query_current_chat="example query"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message with the inline keyboard
    await update.message.reply_text(
        "Click the button below to perform an inline search in this chat:",
        reply_markup=reply_markup
    )

async def add_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /add command."""
    args = context.args  # Extract arguments after the command

    # Check if there are enough arguments
    if len(args) < 2:
        await update.message.reply_text("Usage: /add <amount> <description>")
        return

    amount_str, *description_parts = args
    description = " ".join(description_parts)  # Combine description parts

    try:
        # Validate amount (convert to float)
        amount = float(amount_str)
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please use a number.")
        return

    # Here, you can SAVE the entry to a database or in-memory storage
    # Example: Store in a list (replace with a database)
    entry = {"amount": amount, "description": description}
    # context.user_data.setdefault("entries", []).append(entry)  # User-specific storage

    # Send confirmation
    await update.message.reply_text(f"✅ Added expense: **{amount}** for _{description}_", parse_mode="Markdown")

def main():
    # Create the bot application
    application = Application.builder().token(TOKEN).build()

    # Add a handler for the /start command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_entry))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()

