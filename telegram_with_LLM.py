import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json
import logging
from openai import OpenAI

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")
DEEPSEEK_API = os.getenv("DEEPSEEK_API")

COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Show help"),
]

client = OpenAI(api_key=DEEPSEEK_API, base_url="https://api.deepseek.com")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I am your AI assistant. Send me a message and I will respond.')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /start - Start the bot
    /help - Show this help message
    
    You can also just send me a message and I'll respond to it.
    """
    await update.message.reply_text(help_text)

async def show_loading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show loading animation using answer_callback_query"""
    query = update.callback_query
    if query:
        await query.answer(text="Processing your request...", show_alert=False)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming user messages."""
    user_message = update.message.text
    
    # Create a temporary message with "Loading..." text and a spinner
    loading_message = await update.message.reply_text("⏳ Processing your request...")
    
    try:
        # Show typing action (optional - can be combined with the loading message)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Get response from DeepSeek AI
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_message},
            ],
            stream=False
        )
        
        ai_response = response.choices[0].message.content
        
        # Edit the loading message with the actual response
        await context.bot.edit_message_text(
            chat_id=loading_message.chat_id,
            message_id=loading_message.message_id,
            text=ai_response
        )
        
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        # Edit the loading message with error text
        await context.bot.edit_message_text(
            chat_id=loading_message.chat_id,
            message_id=loading_message.message_id,
            text="⚠️ Sorry, I encountered an error processing your request."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")

async def post_init(application):
    """Set bot commands in Telegram UI"""
    await application.bot.set_my_commands(COMMANDS)

def main():
    """Start the bot."""
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
