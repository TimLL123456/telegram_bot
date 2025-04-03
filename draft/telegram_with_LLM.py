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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming user messages."""
    user_message = update.message.text
    
    # Send the loading animation
    loading_message = await update.message.reply_animation(
        animation="https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif",  # Example loading GIF URL
        caption="Processing your request..."  # Optional caption
    )
    
    try:
        # Get response from DeepSeek AI
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1024,
            stream=False
        )

        ai_response = response.choices[0].message.content
        
        # Delete the loading animation
        await context.bot.delete_message(
            chat_id=loading_message.chat_id,
            message_id=loading_message.message_id
        )
        
        # Send the AI response as a new text message
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        # Delete the loading animation
        await context.bot.delete_message(
            chat_id=loading_message.chat_id,
            message_id=loading_message.message_id
        )
        # Send an error message as a new text
        await update.message.reply_text("⚠️ Sorry, I encountered an error processing your request.")


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
