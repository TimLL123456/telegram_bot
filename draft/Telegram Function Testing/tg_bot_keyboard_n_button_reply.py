#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

import nest_asyncio
nest_asyncio.apply()

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN") 


### Set up logging
def logger_func():
    """Write log"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    return logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("Button 1", callback_data="button_1"),
            InlineKeyboardButton("Button 2", callback_data="button_2"),
            InlineKeyboardButton("Button 3", callback_data="button_3")
        ],
        [
            InlineKeyboardButton("Button 4", callback_data="button_4"),
            InlineKeyboardButton("Button 5", callback_data="button_5"),
            InlineKeyboardButton("Button 6", callback_data="button_6")
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please choose:", reply_markup=reply_markup
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query

    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")


def main() -> None:
    """Run the bot."""

    # Set up logging
    logger = logger_func()

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
