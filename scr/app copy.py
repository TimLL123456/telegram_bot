from llm_tools import TransactionExtractorLLM
from telegram_api import SendMessage
from flask import Flask, Response, request
from supabase_api import *
import json
import config
import requests

app = Flask(__name__)

extractor_llm = TransactionExtractorLLM(model_name="deepseek-chat", temperature=0.0)

# Temporary in-memory storage for demo settings
demo_settings = {}

def _get_api_response_info(api_response: dict) -> tuple[dict, str, str]:
    """
    Retrieves the API response information from the request and determines the update type.
    
    Args:
        api_response (dict): The JSON response from Telegram API.
    
    Returns:
        tuple: (response_info, update_type, user_id)
        - response_info: Dictionary containing relevant data (e.g., text, callback_data).
        - update_type: Type of update ('message', 'edited_message', 'callback_query').
        - user_id: The Telegram user ID.
    
    Raises:
        ValueError: If the update type is unsupported or required data is missing.
    """
    if "message" in api_response:
        update_type = "message"
        message = api_response["message"]
        user_id = str(message["from"]["id"])
        response_info = {
            "text": message.get("text", "").strip(),
            "chat_id": message["chat"]["id"]
        }
    elif "edited_message" in api_response:
        update_type = "edited_message"
        message = api_response["edited_message"]
        user_id = str(message["from"]["id"])
        response_info = {
            "text": message.get("text", "").strip(),
            "chat_id": message["chat"]["id"]
        }
    elif "callback_query" in api_response:
        update_type = "callback_query"
        callback = api_response["callback_query"]
        user_id = str(callback["from"]["id"])
        response_info = {
            "callback_data": callback["data"],
            "chat_id": callback["message"]["chat"]["id"],
            "message_id": callback["message"]["message_id"]
        }
    else:
        raise ValueError("Unsupported update type in Telegram API response.")
    
    return response_info, update_type, user_id

def handle_callback_query(callback_data: str, chat_id: str, user_id: str) -> None:
    """
    Handles callback queries from inline buttons.
    
    Args:
        callback_data (str): The callback data from the inline button.
        chat_id (str): The Telegram chat ID.
        user_id (str): The Telegram user ID.
    """
    if callback_data == 'change_username':
        print(chat_id, user_id)
        demo_settings[user_id]["awaiting_input"] = "username"
        SendMessage(chat_id, "Please send your new username.")
    elif callback_data == 'change_currency':
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "HKD", "callback_data": "currency_HKD"},
                    {"text": "USD", "callback_data": "currency_USD"},
                    {"text": "TWD", "callback_data": "currency_TWD"}
                ]
            ]
        }
        params = {
            "chat_id": chat_id,
            "text": "Please select your default currency:",
            "parse_mode": "HTML",
            "reply_markup": json.dumps(keyboard)
        }
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data=params)
    elif callback_data.startswith('currency_'):
        currency = callback_data.split('_')[1]
        demo_settings[user_id]["default_currency"] = currency
        demo_settings[user_id]["awaiting_input"] = None
        settings_message = (
            f"<b>⚙️ Settings Updated</b>\n\n"
            f"Username: {demo_settings[user_id]['username']}\n"
            f"Default Currency: {currency}"
        )
        SendMessage(chat_id, settings_message)

@app.route('/', methods=['POST', 'GET'])
def telegram():
    if request.method == 'POST':
        try:
            # Retrieve Telegram API response JSON
            tg_api_response = request.get_json()
            if not tg_api_response:
                return Response(status=200)  # Ignore empty requests
            
            print(tg_api_response)
            
            # Parse the API response
            response_info, update_type, tg_user_id = _get_api_response_info(tg_api_response)

            # Initialize demo settings for the user if not present
            if tg_user_id not in demo_settings:
                demo_settings[tg_user_id] = {
                    "username": "Not set",
                    "default_currency": "HKD",
                    "awaiting_input": None
                }

            # Handle settings-related input (e.g., awaiting username input)
            if update_type in ["message", "edited_message"] and demo_settings[tg_user_id].get('awaiting_input') == 'username':
                new_username = response_info["text"]
                demo_settings[tg_user_id]["username"] = new_username
                demo_settings[tg_user_id]["awaiting_input"] = None
                settings_message = (
                    f"<b>⚙️ Settings Updated</b>\n\n"
                    f"Username: {new_username}\n"
                    f"Default Currency: {demo_settings[tg_user_id]['default_currency']}"
                )
                SendMessage(tg_user_id, settings_message)
                return Response(status=200)

            # Handle callback queries
            if update_type == "callback_query":
                handle_callback_query(response_info["callback_data"], response_info["chat_id"], tg_user_id)
                return Response(status=200)

            # Handle commands
            if update_type in ["message", "edited_message"] and response_info["text"].startswith('/'):
                command = response_info["text"].split()[0].lower()
                
                if command == '/start':
                    welcome_message = (
                        "<b>Welcome to the Bookkeeping Bot! 📊</b>\n\n"
                        "I help you track your <i>income</i> and <i>expenses</i>. Just send me transaction details, "
                        "e.g., <code>Spent 50 HKD on 7-11 today</code>, or use commands like <b>/help</b>, <b>/listcategories</b>, <b>/summary</b>, or <b>/settings</b>.\n\n"
                        "If you're a first-time user, please use <b>/regist</b> to set up your account.\n\n"
                    )
                    SendMessage(tg_user_id, welcome_message)
                elif command == '/help':
                    help_message = (
                        "<b>📖 How to Use the Bookkeeping Bot</b>\n\n"
                        "<b>1. Record a transaction</b>: Send a message like <code>Spent 100 HKD on KFC</code> or <code>Received 1000 HKD salary</code>.\n"
                        "<b>2. View categories</b>: Use <b>/listcategories</b> to see your income and expense categories.\n"
                        "<b>3. Get a summary</b>: Use <b>/summary</b> to view your total income and expenses.\n"
                        "<b>4. Adjust settings</b>: Use <b>/settings</b> to update your username and default currency.\n"
                        "<b>5. Need help?</b>: You're already here! Use <b>/help</b> anytime.\n\n"
                        "<i>Note: Ensure your categories exist in the database. Contact support if you need assistance.</i>"
                    )
                    SendMessage(tg_user_id, help_message)
                elif command == '/settings':
                    username = demo_settings[tg_user_id]["username"]
                    default_currency = demo_settings[tg_user_id]["default_currency"]
                    settings_message = (
                        f"<b>⚙️ Your Settings</b>\n\n"
                        f"Username: {username}\n"
                        f"Default Currency: {default_currency}\n\n"
                        f"Use the buttons below to update your settings:"
                    )
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {"text": "Change Username", "callback_data": "change_username"},
                                {"text": "Change Summer", "callback_data": "change_currency"}
                            ]
                        ]
                    }
                    params = {
                        "chat_id": tg_user_id,
                        "text": settings_message,
                        "parse_mode": "HTML",
                        "reply_markup": json.dumps(keyboard)
                    }
                    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
                    requests.post(url, data=params)
                elif command == '/regist':
                    pass  # Implement registration logic if needed

                return Response(status=200)

            # # Handle non-command messages (for demo, assume transaction processing)
            # if update_type in ["message", "edited_message"]:
            #     llm_response = extractor_llm.extract_bookkeeping_features(response_info["text"], tg_user_id)
            #     print("-"*50)
            #     print(f"LLM Response: {llm_response}")

            #     if llm_response["is_transaction"]:
            #         try:
            #             category_id = get_category_id(
            #                 llm_response["category_type"],
            #                 llm_response["category_name"],
            #                 tg_user_id
            #             )
            #             transactions = {
            #                 "user_id": tg_user_id,
            #                 "date": llm_response["date"],
            #                 "category_id": category_id,
            #                 "description": llm_response["description"],
            #                 "currency": llm_response["currency"],
            #                 "amount": llm_response["price"]
            #             }
            #             transaction_insert(transactions)
            #             SendMessage(tg_user_id, "Transaction recorded successfully.")
            #         except Exception as e:
            #             SendMessage(tg_user_id, f"Error recording transaction: {str(e)}")
            #     else:
            #         SendMessage(tg_user_id, "No transaction detected in your message.")

        except Exception as e:
            print(f"Error processing Telegram update: {str(e)}")
            if 'tg_user_id' in locals():
                SendMessage(tg_user_id, f"Error: {str(e)}")
            return Response(status=200)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)