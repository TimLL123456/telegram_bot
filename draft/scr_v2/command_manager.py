import logging
from flask import Response

from telegram_api import *
from supabase_api import *
from utils import *

logger = logging.getLogger(f'flask_app.{__name__}')

@log_function(logger)
class CommandManager:

    def __init__(self, user_settings: dict):
        """Initializes the CommandManager."""
        self.user_settings = user_settings
        self.commands = {
            '/start': self.start,
            '/help': self.help,
            '/ai': self.transaction_parser_llm,
            '/register': self.register,
            '/monthlysummary': self.monthly_summary
        }

    @log_function(logger)
    def command_exec(self, user_command_dict: dict) -> None:
        """
        Executes the command based on user input.

        Args:
            user_command_dict (dict): A dictionary containing user_id and user_input.
        
        Example:
            >>> user_command_dict = {
                    "user_id": 123456789,
                    "command": "/start",
                    "user_input": "/start",
                }
            >>> CommandManager().command_exec(user_command_dict)
        """
        returnable_list = [
            "/ai",
            "/reset"
        ]
        user_id = user_command_dict["user_id"]
        command = user_command_dict["command"]

        if command in self.commands and command in returnable_list:
            return_obj = self.commands[command](user_command_dict)
            return return_obj

        elif command in self.commands:
            self.commands[command](user_command_dict)
            return None

        else:
            SendMessage(user_id, "Unknown command. Please use /help to see available commands.")
    
    @log_function(logger)
    def start(self, user_command_dict: dict) -> None:
        """Handles the /start command to welcome the user."""
        user_id = user_command_dict["user_id"]

        welcome_message = (
            "<b>Welcome to the Bookkeeping Bot! 📊</b>\n"
            "I help you track your <b><i>income</i></b> and <b><i>expenses</i></b>. You can:\n\n"
            "<b>1. Send transaction details:</b>\n"
            "•  <code>/ai Spent 50 HKD on 7-11 today</code>\n"
            "•  <code>/ai KFC 50</code>\n"
            "\n"
            "<b>2. Register or update your account:</b>\n"
            "•  <b>/register</b>\n"
            "\n"
            "<b>3. View a monthly summary:</b>\n"
            "•  <b>/monthlysummary</b>\n"
            "\n"
            "<b>4. Get help anytime:</b>\n"
            "•  <b>/help</b>\n"
            "\n\n"
            "If you're a first-time user, please use <b>/register</b> to set up your account.\n"
        )
        SendMessage(user_id, welcome_message)

    @log_function(logger)
    def help(self, user_command_dict: dict) -> None:
        """Handles the /help command to welcome the user."""
        user_id = user_command_dict["user_id"]

        help_message = (
            "<b>📖 How to Use the Bookkeeping Bot</b>\n"
            "\n\n"
            "<b>1. Record a Transaction</b>:\n"
            "•  Use <code>/ai [description]</code>: <code>/ai KFC 50</code> or <code>/ai Spent 100 HKD on KFC</code> to parse transactions with AI.\n"
            "\n"
            "<b>2. Register or Update Account</b>:\n"
            "•  Use <b>/register</b> to set up or modify your username and default currency.\n"
            "\n"
            "<b>3. View Monthly Summary</b>:\n"
            "•  Use <b>/monthlysummary</b> to view your total income and expenses (under development).\n"
            "\n"
            "<b>4. Need Help?</b>:\n"
            "•  You're already here! Use <b>/help</b> anytime.\n"
            "\n\n"
            "<i>Note: Ensure your account is registered with /register before recording transactions. Contact support if you need assistance.</i>"
        )
        SendMessage(user_id, help_message)

    @log_function(logger)
    def transaction_parser_llm(self, user_command_dict: dict) -> None:
        """Handles the /ai command to parse transactions using LLM."""
        user_id = user_command_dict["user_id"]
        command = user_command_dict["command"]
        user_input = user_command_dict["user_input"]

        # If user_input ("/ai") == command ("/ai")
        if command == user_input:
            guildline_message = (
                "<b><code>/ai</code> Command Guideline for Users</b>\n"
                "<b>Format:</b> <code>/ai [Income / Expense description]</code>\n"
                "<b>Example:</b> <code>/ai KFC 50</code>\n"
                "\n\n"
                "<b><code>/ai</code>指令使用指南</b>\n"
                "<b>格式：</b> <code>/ai [收入/消費 詳情]</code>\n"
                "<b>範例：</b> <code>/ai KFC 50</code>\n"
            )
            SendMessage(user_id, guildline_message)

            return Response(status=200)
        
        SendMessage(user_id, "𝐍𝐨𝐰 𝐥𝐨𝐚𝐝𝐢𝐧𝐠. . .")

        ########################
        # LLM Transaction Parser
        ########################
        # Send user input to the LLM for transaction parsing
        transaction_parser_llm_response = requests.post(
            url=f"http://127.0.0.1:5000/api/transaction_parser_llm",
            json={
                "user_id": user_id,
                "user_input": user_input
            }
        )

        if transaction_parser_llm_response.status_code == 200:

            transaction_parser_llm_response_json = transaction_parser_llm_response.json()
            llm_response = transaction_parser_llm_response_json["data"]["llm_response"]
            transaction = transaction_parser_llm_response_json["data"]["transaction"]
            transaction["category_type"] = llm_response['category_type']
            transaction["category_name"] = llm_response['category_name']

            self.user_settings[user_id]["temp_transaction"] = transaction

            # Insert the transaction into the Supabase database
            # transaction_insert(transaction)

            # Format and send transaction_parse_result
            transaction_parse_result = (
                f"<b>⚙️ AI Transaction Parse Result:</b>\n\n"
                f"<b>User ID:</b> <code>{transaction['user_id']}</code>\n"
                f"<b>Date:</b> <code>{transaction['date']}</code>\n"
                f"<b>Category ID:</b> <code>{transaction['category_id']}</code>\n"
                f"<b>Category Type:</b> <code>{llm_response['category_type']}</code>\n"
                f"<b>Category Name:</b> <code>{llm_response['category_name']}</code>\n"
                f"<b>Description:</b> <code>{transaction['description']}</code>\n"
                f"<b>Currency:</b> <code>{transaction['currency']}</code>\n"
                f"<b>Amount:</b> <code>{transaction['amount']}</code>"
            )

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
            SendInlineKeyboardMessage(user_id, transaction_parse_result, keyboard_setting)

        return self.user_settings
    
    @log_function(logger)
    def register(self, user_command_dict: dict) -> None:
        """Handles the /register command to welcome the user."""
        user_id = user_command_dict["user_id"]

        settings_message = (
            f"<b>⚙️ Your Settings</b>\n\n"
            f"Username: {self.user_settings[user_id]['username']}\n"
            f"Default Currency: {self.user_settings[user_id]['default_currency']}\n\n"
            f"Use the buttons below to update your settings:"
        )

        SettingManager.user_info_setting_keyboard(user_id, settings_message)

    @log_function(logger)
    def monthly_summary(self, user_command_dict: dict) -> None:
        """Handles the /monthlysummary command to welcome the user."""
        user_id = user_command_dict["user_id"]

        monthly_summary_message = (
            "<b>📅 Monthly Summary</b>\n\n"
            f"Please input you user id (<b><code>{user_id}</code></b>) into the website shown to get your report\n\n"
            "This feature is under development. Stay tuned for updates!"
        )

        keyboard_setting = {
            "inline_keyboard": [
                [
                    # {"text": "Open Website", "url": f"http://localhost:8000/?user_id={user_id}"}
                    {"text": "Open Website", "url": f"http://223.18.94.64:8000/?user_id={user_id}"}
                    # {"text": "Open Website", "url": f"https://www.google.com.hk/"}
                ]
            ]
        }

        # SendMessage(user_id, monthly_summary_message)


        SendInlineKeyboardMessage(user_id, monthly_summary_message, keyboard_setting) 