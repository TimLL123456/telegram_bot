from llm_tools import TransactionExtractorLLM
from telegram_api import *
from flask import Flask, Response, request
from supabase_api import *
import json
import requests
import config

app = Flask(__name__)

# Fetch current user settings
user_settings = {}
extractor_llm = TransactionExtractorLLM(model_name="deepseek-chat", temperature=0.0)

def parse_api_response_info(api_response: dict) -> dict:
    """
    Parses the Telegram API response to extract relevant information.
    Args:
        api_response (dict): The JSON response from the Telegram API.
    Returns:
        dict: A dictionary containing the update type and relevant information.   
    """
    
    # Extract relevant information from the API response
    if "message" in api_response:
        update_type = "message"
        response_info = {
            "message": api_response["message"]
        }
    
    elif "edited_message" in api_response:
        update_type = "edited_message"
        response_info = {
            "message": api_response["edited_message"]
        }
    
    elif "callback_query" in api_response:
        update_type = "callback_query"
        response_info = {
            "update_type": update_type,
            "message": api_response["callback_query"]["message"],
            "callback_data": api_response["callback_query"]["data"]
        }
    
    return update_type, response_info


@app.route('/', methods=['POST', "GET"])
def telegram():
    # Handle the incoming POST request from Telegram
    if request.method == 'POST':
        
        # Retrieve telegram api response json
        tg_api_response = request.get_json()
        #print(tg_api_response)  # Uncomment for debugging API response
        update_type, tg_api_response_info = parse_api_response_info(tg_api_response)

        # Retrieve the `user ID` & `user text input` from telegram chatroom api response
        tg_user_id = tg_api_response_info["message"]["chat"]["id"]
        user_input = tg_api_response_info["message"]["text"]

        if not user_settings.get(tg_user_id):
            user_settings[tg_user_id] = {
                "username": None,
                "default_currency": None,
                "option": None
            }
            print(f"New user {tg_user_id} detected. Initializing settings.")

        print(tg_api_response_info["message"])

        # Handle callback queries
        if update_type == "callback_query":
            callback_data = tg_api_response_info["callback_data"]

            if callback_data == "change_username":
                user_settings[tg_user_id]['option'] = 'username'

                print("Change username option selected")

                # Prompt user to change username
                change_username_message = (
                    "<b>🔄 Change Username</b>\n\n"
                    "Please send me your new username:"
                )
                SendMessage(tg_user_id, change_username_message)

            elif callback_data == "change_currency":
                user_settings[tg_user_id]['option'] = 'currency'

                # Prompt user to change currency
                change_currency_message = (
                    "<b>🔄 Change Currency</b>\n\n"
                    "Please send me your new currency:"
                )
                SendMessage(tg_user_id, change_currency_message)
            return Response(status=200)
        
        # Handle settings-related input (e.g., awaiting username or currency input)
        if update_type in ["message", "edited_message"] and user_settings[tg_user_id].get('option') == 'username':
            print("Change username option selected")
            new_username = user_input
            user_settings[tg_user_id]["username"] = new_username
            user_settings[tg_user_id]["option"] = None
            
            username_update_message = (
                f"<b>⚙️ Settings Updated</b>\n\n"
                f"Username: {new_username}\n"
                f"Default Currency: {user_settings[tg_user_id]['default_currency']}"
            )
            SendMessage(tg_user_id, username_update_message)
            return Response(status=200)
        
        elif update_type in ["message", "edited_message"] and user_settings[tg_user_id].get('option') == 'currency':
            new_currency = user_input
            user_settings[tg_user_id]["default_currency"] = new_currency
            user_settings[tg_user_id]["option"] = None
            settings_message = (
                f"<b>⚙️ Settings Updated</b>\n\n"
                f"Username: {user_settings[tg_user_id]['username']}\n"
                f"Default Currency: {new_currency}"
            )
            SendMessage(tg_user_id, settings_message)
            return Response(status=200)

        if user_input.startswith('/'):
            command = user_input.split()[0].lower()
            
            if command == '/start':
                welcome_message = (
                    "<b>Welcome to the Bookkeeping Bot! 📊</b>\n\n"
                    "I help you track your <i>income</i> and <i>expenses</i>. Just send me transaction details, "
                    "e.g., <code>Spent 50 HKD on 7-11 today</code>, or use commands like <b>/help</b>, <b>/listcategories</b>, or <b>/summary</b>.\n\n"
                    "If you're a first-time user, please use <b>/regist</b> to set up your account.\n\n"
                )
                SendMessage(tg_user_id, welcome_message)

            elif command == '/help':
                help_message = (
                    "<b>📖 How to Use the Bookkeeping Bot</b>\n\n"
                    "<b>1. Record a transaction</b>: Send a message like <code>Spent 100 HKD on KFC</code> or <code>Received 1000 HKD salary</code>.\n"
                    "<b>2. View categories</b>: Use <b>/listcategories</b> to see your income and expense categories.\n"
                    "<b>3. Get a summary</b>: Use <b>/summary</b> to view your total income and expenses.\n"
                    "<b>4. Need help?</b>: You're already here! Use <b>/help</b> anytime.\n\n"
                    "<i>Note: Ensure your categories exist in the database. Contact support if you need assistance.</i>"
                )
                SendMessage(tg_user_id, help_message)

            elif command == '/regist':
                if not get_user_info(tg_user_id):  # If user is NOT registered
                    user_settings[tg_user_id] = {
                        "username": None,
                        "default_currency": "HKD",
                        "option": None
                    }
                    username = user_settings[tg_user_id].get('username', 'Not set')
                    default_currency = user_settings[tg_user_id].get('default_currency', 'HKD')
                    
                    # Create inline keyboard for settings
                    settings_message = (
                        f"<b>⚙️ Your Settings</b>\n\n"
                        f"Username: {username}\n"
                        f"Default Currency: {default_currency}\n\n"
                        f"Use the buttons below to update your settings:"
                    )
                    keyboard_setting = {
                        "inline_keyboard": [
                            [
                                {"text": "Change Username", "callback_data": "change_username"},
                                {"text": "Change Currency", "callback_data": "change_currency"}
                            ]
                        ]
                    }
                    SendInlineKeyboardMessage(tg_user_id, settings_message, keyboard_setting)
                else:  # If user is already registered
                    already_registered_message = (
                        "<b>⚠️ You are already registered!</b>\n\n"
                        "If you want to change your settings, use the buttons below:"
                    )
                    keyboard_setting = {
                        "inline_keyboard": [
                            [
                                {"text": "Change Username", "callback_data": "change_username"},
                                {"text": "Change Currency", "callback_data": "change_currency"}
                            ]
                        ]
                    }
                    SendInlineKeyboardMessage(tg_user_id, already_registered_message, keyboard_setting)

            elif command == '/settings':
                # Fetch current user settings
                username = user_settings[tg_user_id].get('username', 'Not set')
                default_currency = user_settings[tg_user_id].get('default_currency', 'HKD')
                
                # Create inline keyboard for settings
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
                            {"text": "Change Currency", "callback_data": "change_currency"}
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


        # # Extracts bookkeeping features by LLM
        # llm_response = extractor_llm.extract_bookkeeping_features(user_input, user_id)

        # # Retrieve the category ID from supabase database
        # category_id = get_category_id(llm_response["category_type"], llm_response["category_name"], user_id)

        # print("-"* 50)
        # print(f"LLM Response: {llm_response}")

        # # If the LLM response indicates a transaction, prepare the transaction data
        # if llm_response["is_transaction"]:
        #     transactions = {
        #         "user_id": user_id,
        #         "date": llm_response["date"],
        #         "category_id": category_id,
        #         "description": llm_response["description"],
        #         "currency": llm_response["currency"],
        #         "amount": llm_response["price"]
        #     }

        #     # Insert the transaction into the Supabase database
        #     transaction_insert(transactions)

        # # Send the LLM response to Telegram
        # SendMessageToTelegram(tg_user_id, llm_response)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)