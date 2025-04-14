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

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Sample data (replace this with your actual data)
ITEMS = [
    "News Article 1",
    "News Article 2",
    "News Article 3",
    "News Article 4",
    "News Article 5",
    "Product A",
    "Product B",
    "Product C",
    "Product D",
    "Product E"
]
ITEMS_PER_PAGE = 3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start command"""
    user = update.message.from_user.first_name
    welcome_message = f"Hello {user}! Welcome to the Pagination Bot. Use /list to see items."
    await update.message.reply_text(welcome_message)

def create_pagination_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Create pagination keyboard with Previous, Next, and page numbers"""
    keyboard = []
    
    # Add Previous button if not on first page
    if page > 0:
        keyboard.append([InlineKeyboardButton("Previous", callback_data=f"prev_{page}")])
    
    # Add page numbers (simplified for this example)
    for i in range(max(0, page - 2), min(total_pages, page + 3)):
        is_current = i == page
        button_text = f"{i + 1}" if not is_current else f"[{i + 1}]"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"page_{i}")])
    
    # Add Next button if not on last page
    if page < total_pages - 1:
        keyboard.append([InlineKeyboardButton("Next", callback_data=f"next_{page}")])
    
    return InlineKeyboardMarkup(keyboard)

async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /list command to show first page of items"""
    page = 0
    total_pages = (len(ITEMS) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_items = ITEMS[start_idx:end_idx]
    
    message = "Here are the items:\n" + "\n".join([f"{i+1}. {item}" for i, item in enumerate(current_items)])
    keyboard = create_pagination_keyboard(page, total_pages)
    
    await update.message.reply_text(message, reply_markup=keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("page_"):
        page = int(data.split("_")[1])
    elif data.startswith("prev_"):
        page = int(data.split("_")[1]) - 1
    elif data.startswith("next_"):
        page = int(data.split("_")[1]) + 1
    else:
        return
    
    total_pages = (len(ITEMS) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    if page < 0 or page >= total_pages:
        await query.edit_message_text("Invalid page!")
        return
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_items = ITEMS[start_idx:end_idx]
    
    message = "Here are the items:\n" + "\n".join([f"{i+1}. {item}" for i, item in enumerate(current_items)])
    keyboard = create_pagination_keyboard(page, total_pages)
    
    await query.edit_message_text(message, reply_markup=keyboard)

def main() -> None:
    """Start the bot"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_items))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
