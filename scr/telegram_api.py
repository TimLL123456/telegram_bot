import config
import requests
import json

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