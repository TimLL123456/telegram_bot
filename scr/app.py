from llm_tools import TransactionExtractorLLM
from telegram_api import *
from flask import Flask, Response, request, jsonify
from supabase_api import *
import json
import requests
import config

app = Flask(__name__)

# Fetch current user settings
user_settings = {}
extractor_llm = TransactionExtractorLLM(model_name="deepseek-chat", temperature=0.0)

def parse_tg_api_respnse_info(api_response: dict) -> dict:
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

@app.route('/api/transaction_parser_llm', methods=['POST'])
def transaction_parser_llm():
    """
    Endpoint to parse transaction details using the LLM.
    Expects a JSON payload with 'user_id' and 'user_input'.
    Returns the parsed transaction details.

    Example payload:
    {
        "user_id": "123456789",
        "user_input": "Spent 50 HKD on 7-11 today"
    }

    Return:
    {
        "message": "Transaction processed successfully",
        "transaction": {
            "user_id": "123456789",
            "date": "2023-10-01",
            "category_id": 1,
            "description": "Spent 50 HKD on 7-11 today",
            "currency": "HKD",
            "amount": 50.0
        },
        "llm_response": {
            "is_transaction": true,
            "date": "2023-10-01",
            "category_type": "Expense",
            "category_name": "Food",
            "description": "Spent 50 HKD on 7-11 today",
            "currency": "HKD",
            "price": 50.0
        }
    }
    """
    # Handle the incoming POST request from Telegram
    if request.method == 'POST':

        # Retrieve and validate JSON payload (user ID and user input) from the request JSON
        transaction_data = request.get_json()

        # Check if the JSON payload contains the required fields
        if (not transaction_data) or ("user_id" not in transaction_data) or ("user_input" not in transaction_data):
            error_message = {
                "error": "Invalid request data",
                "message": "Please provide 'user_id' and 'user_input' in the request body."
            }
            print("Error: Invalid request data.")
            return jsonify(error_message), 400

        user_id = transaction_data.get("user_id")
        user_input = transaction_data.get("user_input")

        # Check if the user ID is valid and registered in the database
        if not get_user_info(user_id):
            error_message = {
                "error": "Invalid user ID",
                "message": "user_id not found in the database. Please register first."
            }
            print("Error: User not registered.")
            return jsonify(error_message), 404

        # Extracts bookkeeping features by LLM
        llm_response = extractor_llm.extract_bookkeeping_features(user_input=user_input, user_id=user_id)

        # Check if the LLM response indicates a transaction
        if llm_response["is_transaction"] is False:
            error_message = {
                "error": "Invalid transaction input",
                "message": f"The input does not contain a valid transaction.\n\nuser input:{user_input}\nuser id: {user_id}"
            }
            print("Error: No transaction detected in the input.")
            return jsonify(error_message), 400

        # Retrieve the category ID from supabase database
        category_id = get_category_id(llm_response["category_type"], llm_response["category_name"], user_id)

        # Check if the category ID is found
        if category_id is None:
            error_message = {
                "error": "Category not found",
                "category_type": llm_response["category_type"],
                "category_name": llm_response["category_name"],
                "user_id": user_id
            }
            print("Error: Category not found in the database.")
            return jsonify(error_message), 404

        print("-"* 50)
        print(f"LLM Response: {llm_response}")

        # If the LLM response indicates a transaction, prepare the transaction data
        transactions = {
            "user_id": user_id,
            "date": llm_response["date"],
            "category_id": category_id,
            "description": llm_response["description"],
            "currency": llm_response["currency"],
            "amount": llm_response["price"]
        }

        # Return success response with transaction and LLM response
        return jsonify({
            "message": "Transaction processed successfully",
            "transaction": transactions,
            "llm_response": llm_response
        }), 200


@app.route('/', methods=['POST', "GET"])
def telegram():
    # Handle the incoming POST request from Telegram
    if request.method == 'POST':
        
        # Retrieve telegram api response json
        tg_api_response = request.get_json()
        #print(tg_api_response)  # Uncomment for debugging API response
        update_type, tg_api_response_info = parse_tg_api_respnse_info(tg_api_response)

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

        # Pass user input to the transaction parser LLM
        transaction_parser_llm_response = requests.post(
            url=f"http://127.0.0.1:5000/api/transaction_parser_llm",
            json={
                "user_id": tg_user_id,
                "user_input": user_input
            }
        )

        if transaction_parser_llm_response.status_code == 200:

            transaction_parser_llm_response_json = transaction_parser_llm_response.json()
            llm_response = transaction_parser_llm_response_json.get("llm_response")
            transaction = transaction_parser_llm_response_json.get("transaction")

            # Insert the transaction into the Supabase database
            transaction_insert(transaction)

            # Send the LLM response to Telegram
            SendMessage(tg_user_id, llm_response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)