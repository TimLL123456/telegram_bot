import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Chat
)

from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackContext
)

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

MAIN_KEYBOARD = [
    ["Browse", "Search"],
    ["Account", "Support"],
    ["Remove Keyboard"]
]

async def send_welcome(update: Update, context: CallbackContext) -> None:
    """Send welcome message with keyboard on first interaction"""
    # Check if we've already welcomed the user
    if context.user_data.get('welcomed'):
        return
        
    reply_markup = ReplyKeyboardMarkup(
        MAIN_KEYBOARD,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Select an option..."
    )
    
    await update.message.reply_text(
        "🌟 Welcome to our bot! How can I help you today?",
        reply_markup=reply_markup
    )
    
    # Mark as welcomed to avoid repeating
    context.user_data['welcomed'] = True

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle all text messages"""
    text = update.message.text
    
    if text == "Remove Keyboard":
        await update.message.reply_text(
            "Keyboard removed. Send any message to bring it back.",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['welcomed'] = False  # Reset to show again on next message
    elif text in ["Browse", "Search", "Account", "Support"]:
        # Handle the menu options
        await update.message.reply_text(
            f"You selected: {text}. Processing your request..."
        )
        # Add your specific logic for each option here
    else:
        # For any other text, show the keyboard again
        await send_welcome(update, context)

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()
    
    # Add handler to show keyboard on first interaction
    # This low-priority handler runs first for any message
    application.add_handler(
        MessageHandler(
            filters.ALL & filters.ChatType.PRIVATE,
            send_welcome
        ),
        group=-1  # Negative group means higher priority
    )
    
    # Add main message handler
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE,
            handle_message
        )
    )
    
    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()
