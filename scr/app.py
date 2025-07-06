from llm_tools import TransactionExtractorLLM
from telegram_api import *
from supabase_api import *
from utils import *
from utils import create_api_response, user_settings_initialize
from command_manager import CommandManager
from callback_manager import CallbackManager

from flask import Flask, Response, request


app = Flask(__name__)

# Fetch current user settings
user_settings = {}
extractor_llm = TransactionExtractorLLM(model_name="deepseek-chat", temperature=0.0)


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
        "status": "success" | "error",
        "message": "success message" | "error message",
        "data": {
            "transaction": {...},
            "llm_response": {...}
        } | null,
        "error": {
            "code": "ERROR_CODE",
            "details": {...}
        } | null
    }
    """
    # Handle the incoming POST request from Telegram
    if request.method == 'POST':

        # Retrieve and validate JSON payload (user ID and user input) from the request JSON
        transaction_data = request.get_json()

        # Check if the JSON payload contains the required fields
        if (not transaction_data) or ("user_id" not in transaction_data) or ("user_input" not in transaction_data):
            return create_api_response(
                status="error",
                message="Please provide 'user_id' and 'user_input' in the request body",
                error={
                    "code": "INVALID_REQUEST",
                    "details": transaction_data
                },
                http_status=400
            )

        user_id = transaction_data.get("user_id")
        user_input = transaction_data.get("user_input")

        # Check if the user ID is valid and registered in the database
        if get_user_info(user_id) is None:
            return create_api_response(
                status="error",
                message="user_id not found in the database. Please register first",
                error={
                    "code": "USER_NOT_FOUND",
                    "details": transaction_data
                },
                http_status=404
            )

        # Extracts bookkeeping features by LLM
        llm_response = extractor_llm.extract_bookkeeping_features(user_input=user_input, user_id=user_id)

        # Check if the LLM response indicates a transaction
        if llm_response["is_transaction"] is False:
            return create_api_response(
                status="error",
                message="The input does not contain a valid transaction",
                error={
                    "code": "INVALID_TRANSACTION",
                    "details": transaction_data
                },
                http_status=400
            )

        # Retrieve the category ID from supabase database
        category_id = get_category_id(llm_response["category_type"], llm_response["category_name"], user_id)

        # Check if the category ID is found
        if category_id is None:
            return create_api_response(
                status="error",
                message="Category not found in the database",
                error={
                    "code": "CATEGORY_NOT_FOUND",
                    "details": transaction_data
                },
                http_status=404
            )

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
        return create_api_response(
            status="success",
            message="Transaction processed successfully",
            data={
                "transaction": transactions,
                "llm_response": llm_response
            },
            http_status=200
        )


@app.route('/', methods=['POST'])
def telegram():
    # Handle the incoming POST request from Telegram
    if request.method == 'POST':

        global user_settings

        ##################################
        # Set Command and Callback Manager
        ##################################
        command_manager = CommandManager(user_settings)
        callback_manager = CallbackManager(user_settings)
        
        ##################################
        # Telgram API Response Processiong
        ##################################
        tg_api_response = request.get_json() # Retrieve telegram api response json
        update_type, tg_api_response_info = parse_tg_api_respnse_info(tg_api_response)

        # Retrieve the `user ID` & `user text input` from telegram chatroom api response
        tg_user_id = tg_api_response_info["message"]["chat"]["id"]
        user_input = tg_api_response_info["message"]["text"]
        
        # Temporary information store
        if tg_user_id not in user_settings:
            user_settings = user_settings_initialize(tg_user_id, user_settings)

        ###########################
        # User Info Default Setting
        ###########################
        setting_manager = SettingManager(
            user_settings=user_settings,
            user_id=tg_user_id,
            user_input=user_input
        )

        print("-"*50)
        print(user_settings)

        if update_type in ["message", "edited_message"] and user_settings[tg_user_id].get('option') == 'REGISTER_username':
            user_settings = setting_manager.username_update()
            return Response(status=200)
        
        elif update_type in ["message", "edited_message"] and user_settings[tg_user_id].get('option') == 'REGISTER_currency':
            user_settings = setting_manager.currency_update()
            return Response(status=200)
        
        elif update_type in ["message", "edited_message"] and user_settings[tg_user_id].get('option') == 'TRANSACTION_date':
            user_settings = setting_manager.date_update()
            return Response(status=200)

        ########################
        # Handle command queries
        ########################
        if user_input.startswith('/'):
            command = user_input.split(maxsplit=1)[0].lower()
            user_transaction_input = user_input.split(maxsplit=1)[-1]

            user_command_dict = {
                "user_id": tg_user_id,
                "command": command,
                "user_input": user_transaction_input,
                "user_settings": user_settings
            }

            return_obj = command_manager.command_exec(user_command_dict=user_command_dict)

            # Update user_settings dictionary if command data in returnable_list
            if return_obj is not None:
                user_settings = return_obj

            return Response(status=200)

        #########################
        # Handle callback queries
        #########################
        if update_type == "callback_query":
            callback_data = tg_api_response_info["callback_data"]

            user_callback_dict = {
                "user_id": tg_user_id,
                "callback_data": callback_data
            }

            return_obj = callback_manager.callback_exec(user_callback_dict=user_callback_dict)
            
            # Update user_settings dictionary if callback data in returnable_list
            if return_obj is not None:
                user_settings = return_obj

            return Response(status=200)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)