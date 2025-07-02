from telegram_api import *

class CallbackManager:
    
    def __init__(self, user_settings: dict):
        """Initializes the CommandManager."""
        self.user_settings = user_settings
        self.callbacks = {
            "REGISTER_change_username": self.REGISTER_change_username,
            "REGISTER_change_currency": self.REGISTER_change_currency,
            "TRANSACTION_change_date": self.TRANSACTION_change_date,
            "TRANSACTION_category_type": self.TRANSACTION_category_type,
            "TRANSACTION_description": self.TRANSACTION_description,
            "TRANSACTION_currency": self.TRANSACTION_currency,
            "TRANSACTION_amount": self.TRANSACTION_amount
        }
    
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
            "REGISTER_change_username", "REGISTER_change_currency"
        ]
        callback_data = user_callback_dict["callback_data"]
        
        if callback_data in self.callbacks:
            return_obj = self.callbacks[callback_data](user_callback_dict)

            if callback_data not in returnable_list:
                return_obj = None
        
        return return_obj

    def REGISTER_change_username(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'username'

        # Prompt user to change username
        change_username_message = (
            "<b>🔄 Change Username</b>\n\n"
            "Please send me your new username:"
        )
        SendMessage(user_id, change_username_message)

        return self.user_settings

    def REGISTER_change_currency(self, user_callback_dict: dict) -> None:
        user_id = user_callback_dict["user_id"]
        self.user_settings[user_id]['option'] = 'currency'

        # Prompt user to change currency
        change_currency_message = (
            "<b>🔄 Change Currency</b>\n\n"
            "Please send me your new currency:"
        )
        SendMessage(user_id, change_currency_message)

        return self.user_settings
    
    def TRANSACTION_change_date(self):
        pass

    def TRANSACTION_category_type(self):
        pass

    def TRANSACTION_description(self):
        pass

    def TRANSACTION_currency(self):
        pass

    def TRANSACTION_amount(self):
        pass
