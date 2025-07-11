import json
import logging
import functools
from dateutil import parser

from telegram_api import *
from supabase_api import *

logger = logging.getLogger(f'flask_app.{__name__}')

def logger_setup(
    logger_name:str,
    logger_filename:str,
    log_console_format:str = '%(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    log_file_format:str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
):
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_console_format)
    console_handler.setFormatter(console_formatter)

    # Create rotating file handler
    file_handler = logging.FileHandler(logger_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_file_format)
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def log_function(logger:logging):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering function '{func.__name__}' with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"Exiting function '{func.__name__}' with result={result}")
            return result
        return wrapper
    return decorator

def log_api(logger:logging):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info("="*100)
            logger.debug(f"Entering function '{func.__name__}' with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"Exiting function '{func.__name__}' with result={result}")
            logger.info("="*100)
            return result
        return wrapper
    return decorator

@log_function(logger)
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

@log_function(logger)
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

@log_function(logger)
def stardardize_date(date_input:str):
    try:
        # Parse the input date string
        parsed_date = parser.parse(date_input)

        # Format to YYYY-MM-DD
        return parsed_date.strftime("%Y-%m-%d")
    
    except ValueError:
        return None

############################################################################################################
############################################################################################################

@log_function(logger)
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
                    {"text": "Change Category Name", "callback_data": "TRANSACTION_category_name"}
                ],
                [
                    {"text": "Change Description", "callback_data": "TRANSACTION_description"}
                ],
                [
                    {"text": "Change Currency", "callback_data": "TRANSACTION_currency"}
                ],
                [
                    {"text": "Change Amount", "callback_data": "TRANSACTION_amount"}
                ],
                [
                    {"text": "Save", "callback_data": "TRANSACTION_save"}
                ]
            ]
        }

        SendInlineKeyboardMessage(user_id, transaction_update_message, keyboard_setting)

    @log_function(logger)
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
    
    @log_function(logger)
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

    @log_function(logger)
    def trans_date_update(self):
        new_date = self.user_input
        new_date = stardardize_date(new_date)

        if new_date is None:
            SendMessage(self.user_id, f"Cannot identify the date format ({self.user_input}). Please input again!")
            return self.user_settings

        self.user_settings[self.user_id]["temp_transaction"]["date"] = new_date
        self.user_settings[self.user_id]["option"] = None

        temp_transaction = self.user_settings[self.user_id]["temp_transaction"]

        date_update_message = (
            f"<b>⚙️ Updated Transaction Result:</b>\n\n"
            f"<b>User ID:</b> <code>{temp_transaction['user_id']}</code>\n"
            f"<b>Date:</b> <code>{temp_transaction['date']}</code>\n"
            f"<b>Category Type:</b> <code>{temp_transaction['category_type']}</code>\n"
            f"<b>Category Name:</b> <code>{temp_transaction['category_name']}</code>\n"
            f"<b>Description:</b> <code>{temp_transaction['description']}</code>\n"
            f"<b>Currency:</b> <code>{temp_transaction['currency']}</code>\n"
            f"<b>Amount:</b> <code>{temp_transaction['amount']}</code>"
        )

        SettingManager.transaction_setting_keyboard(self.user_id, date_update_message)

        return self.user_settings

    @log_function(logger)
    def trans_category_type_update(self):
        new_category_type = self.user_input
        self.user_settings[self.user_id]["temp_transaction"]["category_type"] = new_category_type
        self.user_settings[self.user_id]["option"] = None

        temp_transaction = self.user_settings[self.user_id]["temp_transaction"]

        category_type_update_message = (
            f"<b>⚙️ Updated Transaction Result:</b>\n\n"
            f"<b>User ID:</b> <code>{temp_transaction['user_id']}</code>\n"
            f"<b>Date:</b> <code>{temp_transaction['date']}</code>\n"
            f"<b>Category Type:</b> <code>{temp_transaction['category_type']}</code>\n"
            f"<b>Category Name:</b> <code>{temp_transaction['category_name']}</code>\n"
            f"<b>Description:</b> <code>{temp_transaction['description']}</code>\n"
            f"<b>Currency:</b> <code>{temp_transaction['currency']}</code>\n"
            f"<b>Amount:</b> <code>{temp_transaction['amount']}</code>"
        )

        SettingManager.transaction_setting_keyboard(self.user_id, category_type_update_message)

        return self.user_settings

    @log_function(logger)
    def trans_category_name_update(self):
        new_category_name = self.user_input
        self.user_settings[self.user_id]["temp_transaction"]["category_name"] = new_category_name

        category_type = self.user_settings[self.user_id]["temp_transaction"]["category_type"]
        category_name = self.user_settings[self.user_id]["temp_transaction"]["category_name"]

        ########################
        # Validate category name
        ########################
        category_id = get_category_id(category_type, category_name, self.user_id)
        if category_id is None:
            categories_info_list = [record[1] for record in get_user_categories_info(self.user_id) if record[0] == category_type]

            reminder_message = (
              "Cannot found the category name in database. Please input the category name from below:\n\n"
            )

            for category in categories_info_list:
              reminder_message += f"• <code>{category}</code>\n"
            
            SendMessage(self.user_id, reminder_message)

            return self.user_settings

        self.user_settings[self.user_id]["option"] = None

        temp_transaction = self.user_settings[self.user_id]["temp_transaction"]

        category_name_update_message = (
            f"<b>⚙️ Updated Transaction Result:</b>\n\n"
            f"<b>User ID:</b> <code>{temp_transaction['user_id']}</code>\n"
            f"<b>Date:</b> <code>{temp_transaction['date']}</code>\n"
            f"<b>Category Type:</b> <code>{temp_transaction['category_type']}</code>\n"
            f"<b>Category Name:</b> <code>{temp_transaction['category_name']}</code>\n"
            f"<b>Description:</b> <code>{temp_transaction['description']}</code>\n"
            f"<b>Currency:</b> <code>{temp_transaction['currency']}</code>\n"
            f"<b>Amount:</b> <code>{temp_transaction['amount']}</code>"
        )

        SettingManager.transaction_setting_keyboard(self.user_id, category_name_update_message)

        return self.user_settings

    @log_function(logger)
    def trans_description_update(self):
        new_description = self.user_input
        self.user_settings[self.user_id]["temp_transaction"]["description"] = new_description
        self.user_settings[self.user_id]["option"] = None

        temp_transaction = self.user_settings[self.user_id]["temp_transaction"]

        description_update_message = (
            f"<b>⚙️ Updated Transaction Result:</b>\n\n"
            f"<b>User ID:</b> <code>{temp_transaction['user_id']}</code>\n"
            f"<b>Date:</b> <code>{temp_transaction['date']}</code>\n"
            f"<b>Category Type:</b> <code>{temp_transaction['category_type']}</code>\n"
            f"<b>Category Name:</b> <code>{temp_transaction['category_name']}</code>\n"
            f"<b>Description:</b> <code>{temp_transaction['description']}</code>\n"
            f"<b>Currency:</b> <code>{temp_transaction['currency']}</code>\n"
            f"<b>Amount:</b> <code>{temp_transaction['amount']}</code>"
        )

        SettingManager.transaction_setting_keyboard(self.user_id, description_update_message)

        return self.user_settings

    @log_function(logger)
    def trans_currency_update(self):
        new_currency = self.user_input
        self.user_settings[self.user_id]["temp_transaction"]["currency"] = new_currency
        self.user_settings[self.user_id]["option"] = None

        temp_transaction = self.user_settings[self.user_id]["temp_transaction"]

        currency_update_message = (
            f"<b>⚙️ Updated Transaction Result:</b>\n\n"
            f"<b>User ID:</b> <code>{temp_transaction['user_id']}</code>\n"
            f"<b>Date:</b> <code>{temp_transaction['date']}</code>\n"
            f"<b>Category Type:</b> <code>{temp_transaction['category_type']}</code>\n"
            f"<b>Category Name:</b> <code>{temp_transaction['category_name']}</code>\n"
            f"<b>Description:</b> <code>{temp_transaction['description']}</code>\n"
            f"<b>Currency:</b> <code>{temp_transaction['currency']}</code>\n"
            f"<b>Amount:</b> <code>{temp_transaction['amount']}</code>"
        )

        SettingManager.transaction_setting_keyboard(self.user_id, currency_update_message)

        return self.user_settings

    @log_function(logger)
    def trans_amount_update(self):
        new_amount = self.user_input
        self.user_settings[self.user_id]["temp_transaction"]["amount"] = new_amount
        self.user_settings[self.user_id]["option"] = None

        temp_transaction = self.user_settings[self.user_id]["temp_transaction"]

        amount_update_message = (
            f"<b>⚙️ Updated Transaction Result:</b>\n\n"
            f"<b>User ID:</b> <code>{temp_transaction['user_id']}</code>\n"
            f"<b>Date:</b> <code>{temp_transaction['date']}</code>\n"
            f"<b>Category Type:</b> <code>{temp_transaction['category_type']}</code>\n"
            f"<b>Category Name:</b> <code>{temp_transaction['category_name']}</code>\n"
            f"<b>Description:</b> <code>{temp_transaction['description']}</code>\n"
            f"<b>Currency:</b> <code>{temp_transaction['currency']}</code>\n"
            f"<b>Amount:</b> <code>{temp_transaction['amount']}</code>"
        )

        SettingManager.transaction_setting_keyboard(self.user_id, amount_update_message)

        return self.user_settings