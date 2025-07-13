import config
import requests
import json

def parse_tg_api_respnse_info(api_response: dict) -> tuple:
    """
    Parses the Telegram API response to extract relevant information.

    Args:
        api_response (dict): The JSON response from the Telegram API.

    Returns:
        tuple: A tuple containing the update type and relevant information.   
    """

    update_type, response_info = None, {}
    
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

def SendMessage(tg_user_id:int, message:dict) -> None:
    """
    Sends a message to a Telegram chat using the bot API.
    
    Args:
        message (dict): The response from the LLM containing the message to send.
    """

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

    params = {
        "chat_id": tg_user_id,
        "text": str(message),
        "parse_mode": "HTML"
    }

    requests.post(url, data=params)

def SendInlineKeyboardMessage(tg_user_id:int, message:str, keyboard_setting:dict) -> None:
    """
    Sends a message with an inline keyboard to a Telegram chat.

    Args:
        tg_user_id (int): The Telegram user ID to send the message to.
        keyboard_setting (dict): The inline keyboard settings in JSON format.

    Example:
        keyboard_setting = {
            "inline_keyboard": [
                [
                    {"text": "Change Username", "callback_data": "change_username"},
                    {"text": "Change Currency", "callback_data": "change_currency"}
                ]
            ]
        }
    """
    params = {
        "chat_id": tg_user_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard_setting)
    }
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data=params)

def transaction_parser_llm(user_id: int, user_input: str):
    """
    Sends user input to the LLM for transaction parsing.

    Args:
        user_id (int): The ID of the user making the request.
        user_input (str): The input text from the user to be parsed.
    
    Returns:
        dict: The JSON response from the LLM API containing the parsed transaction data.
    
    Example:
        >>> transaction_parser_llm(4, "Sample transaction text")
        >>> {'status': 'success',
            'message': 'Transaction processed successfully',
            'data': {
                'transaction': {
                    'user_id': 1,
                    'date': '2025-07-01',
                    'category_id': 16,
                    'description': "M記 (McDonald's)",
                    'currency': 'HKD',
                    'amount': 50.0
                },
                'llm_response': {
                    'is_transaction': True,
                    'date': '2025-07-01',
                    'category_type': 'Expense',
                    'category_name': 'Food',
                    'description': "M記 (McDonald's)",
                    'currency': 'HKD',
                    'price': 50.0
                }
            },
            'error': None}
    """

    response = requests.post(
        url="http://127.0.0.1:5000/api/transaction_parser_llm",
        json={
            "user_id": user_id,
            "user_input": user_input
        }
    )

    return response.json()