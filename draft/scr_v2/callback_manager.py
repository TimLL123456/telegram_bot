import logging

from utils import *
from telegram_api import *

logger = logging.getLogger(f'flask_app.{__name__}')

@log_function(logger)
class CallbackManager:
    
    def __init__(self, user_settings: dict):
        """Initializes the CommandManager."""
        self.user_settings = user_settings
        self.callbacks = {
            "REGISTER_change_username": self.REGISTER_change_username,
            "REGISTER_change_currency": self.REGISTER_change_currency,
            "TRANSACTION_change_date": self.TRANSACTION_change_date,
            "TRANSACTION_category_type": self.TRANSACTION_category_type,
            "TRANSACTION_category_name": self.TRANSACTION_category_name,
            "TRANSACTION_description": self.TRANSACTION_description,
            "TRANSACTION_currency": self.TRANSACTION_currency,
            "TRANSACTION_amount": self.TRANSACTION_amount,
            "TRANSACTION_save": self.TRANSACTION_save
        }

    @log_function(logger)
    def callback_exec(self, user_callback_dict: dict) -> None | dict:
        """
        Executes the callback based on user input.

        Args:
            user_callback_dict (dict): A dictionary containing user callback details.

        Example:
            >>> user_callback_dict = {
                    "user_id": 123456789,
                    "callback_data": "change_username"
                }
            >>> CallbackManager().callback_exec(user_callback_dict)
        """
        returnable_list = [
            "REGISTER_change_username",
            "REGISTER_change_currency",
            "TRANSACTION_change_date",
            "TRANSACTION_category_type",
            "TRANSACTION_category_name",
            "TRANSACTION_description",
            "TRANSACTION_currency",
            "TRANSACTION_amount"
        ]
        callback_data = user_callback_dict["callback_data"]
        
        if callback_data in self.callbacks:
            return_obj = self.callbacks[callback_data](user_callback_dict) if callback_data in returnable_list else None
            return return_obj
    
    @log_function(logger)
    def REGISTER_change_username(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'REGISTER_username'

        # Prompt user to change username
        change_username_message = (
            "<b>🔄 Change Username</b>\n\n"
            "Please send me your new username:"
        )
        SendMessage(user_id, change_username_message)

        return self.user_settings

    @log_function(logger)
    def REGISTER_change_currency(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'REGISTER_currency'

        # Prompt user to change currency
        change_currency_message = (
            "<b>🔄 Change Currency</b>\n\n"
            "Please send me your new currency:"
        )
        SendMessage(user_id, change_currency_message)

        return self.user_settings
    
    @log_function(logger)
    def TRANSACTION_change_date(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'TRANSACTION_date'

        # Prompt user to change currency
        change_date_message = (
            "<b>🔄 Change Date</b>\n\n"
            "Please send me the correct date:"
        )
        SendMessage(user_id, change_date_message)

        return self.user_settings
    
    @log_function(logger)
    def TRANSACTION_category_type(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'TRANSACTION_category_type'

        # Prompt user to change currency
        change_category_type_message = (
            "<b>🔄 Change Category Type</b>\n\n"
            "Please send me the correct category type:"
        )
        SendMessage(user_id, change_category_type_message)

        return self.user_settings

    @log_function(logger)
    def TRANSACTION_category_name(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'TRANSACTION_category_name'

        # Prompt user to change currency
        change_category_type_message = (
            "<b>🔄 Change Category Name</b>\n\n"
            "Please send me the correct category type:"
        )
        SendMessage(user_id, change_category_type_message)

        return self.user_settings

    @log_function(logger)
    def TRANSACTION_description(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'TRANSACTION_description'

        # Prompt user to change currency
        change_description_message = (
            "<b>🔄 Change Description</b>\n\n"
            "Please send me the correct description:"
        )
        SendMessage(user_id, change_description_message)

        return self.user_settings

    @log_function(logger)
    def TRANSACTION_currency(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'TRANSACTION_currency'

        # Prompt user to change currency
        change_currency_message = (
            "<b>🔄 Change Currency</b>\n\n"
            "Please send me the correct currency:"
        )
        SendMessage(user_id, change_currency_message)

        return self.user_settings

    @log_function(logger)
    def TRANSACTION_amount(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'TRANSACTION_amount'

        # Prompt user to change currency
        change_amount_message = (
            "<b>🔄 Change Amount</b>\n\n"
            "Please send me the correct amount:"
        )
        SendMessage(user_id, change_amount_message)

        return self.user_settings

    @log_function(logger)
    def TRANSACTION_save(self, user_callback_dict: dict) -> None:

        # Prompt user to change currency
        change_amount_message = (
            "Transaction have been saved!"
            "\n\n"
            "You may click <b>/start</b> or <b>/help</b> to get more information."
        )
        SendMessage(user_id, change_amount_message)


