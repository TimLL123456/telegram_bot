from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Define your bot commands (these appear in Telegram's menu)
COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Show help"),
    BotCommand("menu", "Show this menu"),
    BotCommand("settings", "Change settings")
]

# Keyboard with just a Menu button
MENU_KEYBOARD = [["📋 Show Commands"]]

async def post_init(application):
    """Set bot commands in Telegram UI"""
    await application.bot.set_my_commands(COMMANDS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with persistent menu"""
    reply_markup = ReplyKeyboardMarkup(
        MENU_KEYBOARD,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Tap 'Show Commands' or type /help"
    )
    await update.message.reply_text(
        "Welcome! Here's what you can do:",
        reply_markup=reply_markup
    )

async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display all commands when menu button is pressed"""
    commands_text = "\n".join(
        f"/{cmd.command} - {cmd.description}" 
        for cmd in COMMANDS
    )
    await update.message.reply_text(
        f"📚 Available commands:\n\n{commands_text}"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command (same as menu button)"""
    await show_commands(update, context)

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", help_command))  # Alias for /help
    
    # Handle menu button press
    app.add_handler(MessageHandler(
        filters.Text(["📋 Show Commands"]), 
        show_commands
    ))
    
    app.run_polling()

if __name__ == "__main__":
    main()