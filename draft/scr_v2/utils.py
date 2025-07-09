import json
import yaml
import logging
import logging.config

from telegram_api import *
from supabase_api import *

def setup_logger():
    with open("logging_config.yml", 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

def create_api_response(
    status: str,
    message: str,
    data: dict = None,
    error: str = None,
    http_status: int = 200
) -> tuple:
    """
    Helper function to create a standardized API response.

    Args:
        status (str): Status of the response ('success' or 'error').
        message (str): Human-readable message describing the result.
        data (dict, optional): Data to include in successful responses.
        error (dict, optional): Error details for error responses.
        http_status (int): HTTP status code for the response.

    Returns:
        tuple: JSON response and HTTP status code.
    """
    response = {
        "status": status,
        "message": message,
        "data": data,
        "error": error
    }

    return json.dumps(response), http_status

def user_settings_initialize(user_id: int, user_settings_dict: dict) -> dict:
    """Initialize user settings for a new user."""
    user_setting_database = get_user_info(user_id)
    if user_setting_database:
        user_settings_dict[user_id] = {
            "username": user_setting_database["username"],
            "default_currency": user_setting_database["default_currency"],
            "temp_transaction": None,
            "option": None
        }
    else:
        user_settings_dict[user_id] = {
            "username": None,
            "default_currency": None,
            "temp_transaction": None,
            "option": None
        }
    
    return user_settings_dict

class SettingManager:

    def __init__(
        self,
        user_settings: dict,
        user_id: int,
        user_input: str
    ):
        self.user_settings = user_settings
        self.user_id = user_id
        self.user_input = user_input

    @staticmethod
    def user_info_setting_keyboard(user_id, user_info_update_message):
        keyboard_setting = {
            "inline_keyboard": [
                [
                    {"text": "Change Username", "callback_data": "REGISTER_change_username"},
                    {"text": "Change Currency", "callback_data": "REGISTER_change_currency"}
                ]
            ]
        }

        SendInlineKeyboardMessage(user_id, user_info_update_message, keyboard_setting)
        
    @staticmethod
    def transaction_setting_keyboard(user_id, transaction_update_message):
        keyboard_setting = {
            "inline_keyboard": [
                [
                    {"text": "Change Date", "callback_data": "TRANSACTION_change_date"}
                ],
                [
                    {"text": "Change Category Type", "callback_data": "TRANSACTION_category_type"}
                ],
                [
                    {"text": "Change Description", "callback_data": "TRANSACTION_description"}
                ],
                [
                    {"text": "Change Currency", "callback_data": "TRANSACTION_currency"}
                ],
                [
                    {"text": "Change Amount", "callback_data": "TRANSACTION_amount"}
                ]
            ]
        }

        SendInlineKeyboardMessage(user_id, transaction_update_message, keyboard_setting)

    def username_update(self):
        new_username = self.user_input
        self.user_settings[self.user_id]["username"] = new_username
        self.user_settings[self.user_id]["option"] = None
        
        username_update_message = (
            f"<b>⚙️ Settings Updated</b>\n\n"
            f"Username: {new_username}\n"
            f"Default Currency: {self.user_settings[self.user_id]['default_currency']}"
        )

        SettingManager.user_info_setting_keyboard(self.user_id, username_update_message)

        user_info_update(
            user_id=self.user_id,
            username=new_username
        )

        return self.user_settings
    
    def currency_update(self):
        new_currency = self.user_input
        self.user_settings[self.user_id]["currency"] = new_currency
        self.user_settings[self.user_id]["option"] = None

        currency_update_message = (
            f"<b>⚙️ Settings Updated</b>\n\n"
            f"Username: {self.user_settings[self.user_id]['username']}\n"
            f"Default Currency: {new_currency}"
        )

        SettingManager.user_info_setting_keyboard(self.user_id, currency_update_message)

        user_info_update(
            user_id=self.user_id,
            currency=new_currency
        )

        return self.user_settings
    
    def date_update(self):
        new_date = self.user_input
        self.user_settings[self.user_id]["temp_transaction"]["date"] = new_date
        self.user_settings[self.user_id]["option"] = None

        date_update_message = (
            f"<b>⚙️ Settings Updated</b>\n\n"
            f"Username: {self.user_settings[self.user_id]['username']}\n"
            f"Updated date: {new_date}"
        )

        SettingManager.transaction_setting_keyboard(self.user_id, date_update_message)

        return self.user_settings