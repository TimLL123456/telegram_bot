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

# Custom parse_expense function (simulating LLM output)
def parse_expense(message_text):
    try:
        # For testing, we'll hardcode a simple parser that assumes the input is "Description Amount [on Date]"
        parts = message_text.split()
        description = "Unknown"
        amount = "0"
        date = "Today"

        if len(parts) >= 2:
            description = " ".join(parts[:-1]) if parts[-1].isdigit() else " ".join(parts[:-2])
            if parts[-1].isdigit():
                amount = parts[-1]
            if "on" in message_text.lower() and parts[-1].isdigit():
                date_index = message_text.lower().find("on") + 3
                date = message_text[date_index:].strip() if date_index > 0 else "Today"

        return {
            "description": description,
            "amount": amount,
            "date": date
        }
    except Exception as e:
        logger.error(f"Error in parse_expense: {e}")
        return {"description": "Error", "amount": "0", "date": "Today"}

def create_edit_keyboard(parsed_data):
    try:
        # Convert parsed_data dict to a short string identifier for callback_data
        # Use a unique string or ID instead of the entire dict
        data_id = f"data_{hash(str(parsed_data))}"  # Create a unique identifier
        keyboard = [
            [InlineKeyboardButton("Edit Description", callback_data=f"edit_desc|{data_id}")],
            [InlineKeyboardButton("Edit Amount", callback_data=f"edit_amount|{data_id}")],
            [InlineKeyboardButton("Edit Date", callback_data=f"edit_date|{data_id}")],
            [InlineKeyboardButton("Confirm", callback_data=f"confirm|{data_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    except Exception as e:
        logger.error(f"Error in create_edit_keyboard: {e}")
        return InlineKeyboardMarkup([])  # Return empty keyboard on error

async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_message = update.message.text
        parsed_data = parse_expense(user_message)

        # Store parsed data in user context for later use
        context.user_data['current_data'] = parsed_data

        # Display parsed data and offer editing options
        await update.message.reply_text(
            f"*Parsed Expense:*\n"
            f"- Description: {parsed_data['description']}\n"
            f"- Amount: ${parsed_data['amount']}\n"
            f"- Date: {parsed_data['date']}\n\n"
            f"Is this correct? Edit if needed.",
            reply_markup=create_edit_keyboard(parsed_data),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in handle_expense: {e}")
        await update.message.reply_text("An error occurred while processing your expense. Please try again.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()

        data = query.data
        parts = data.split("|")
        action = parts[0]
        data_id = parts[1] if len(parts) > 1 else None

        if action == "confirm":
            parsed_data = context.user_data.get('current_data', {})
            await query.edit_message_text(
                f"Expense confirmed and saved!\n"
                f"Description: {parsed_data.get('description', 'Unknown')}\n"
                f"Amount: ${parsed_data.get('amount', '0')}\n"
                f"Date: {parsed_data.get('date', 'Today')}"
            )
        elif action.startswith("edit_"):
            field = action.replace("edit_", "")
            parsed_data = context.user_data.get('current_data', {})

            await query.edit_message_text(
                f"Current {field}: {parsed_data.get(field, 'Not set')}\nSend the new {field} value:"
            )
            context.user_data['waiting_for_edit'] = field
            context.user_data['last_message_id'] = query.message.message_id
            context.user_data['chat_id'] = query.message.chat_id

    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        await query.answer("An error occurred. Please try again.")

async def handle_edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if 'waiting_for_edit' in context.user_data:
            new_value = update.message.text
            field = context.user_data['waiting_for_edit']
            parsed_data = context.user_data.get('current_data', {})

            # Update the parsed data
            parsed_data[field] = new_value
            context.user_data['current_data'] = parsed_data

            # Send updated data back with edit options
            await update.message.reply_text(
                f"*Updated Expense:*\n"
                f"- Description: {parsed_data['description']}\n"
                f"- Amount: ${parsed_data['amount']}\n"
                f"- Date: {parsed_data['date']}\n\n"
                f"Confirm changes?",
                reply_markup=create_edit_keyboard(parsed_data),
                parse_mode='Markdown'
            )

            # Clean up state
            del context.user_data['waiting_for_edit']

    except Exception as e:
        logger.error(f"Error in handle_edit_input: {e}")
        await update.message.reply_text("An error occurred while updating your expense. Please try again.")

def main() -> None:
    try:
        application = Application.builder().token(TOKEN).build()

        # Add handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_input))

        # Start the Bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main()