from telegram_api import *
from supabase_api import *
from flask import Response

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

    def command_exec(self, user_command_dict: dict) -> None:
        """
        Executes the command based on user input.

        Args:
            user_command_dict (dict): A dictionary containing user_id and user_input.
        
        Example:
            >>> user_command_dict = {
                    "user_id": 123456789,
                    "command": "/start",
                    "user_input": "/start"
                }
            >>> CommandManager().command_exec(user_command_dict)
        """
        user_id = user_command_dict["user_id"]
        command = user_command_dict["command"]

        if command in self.commands:
            self.commands[command](user_command_dict)
        else:
            SendMessage(user_id, "Unknown command. Please use /help to see available commands.")
    
    def start(self, user_command_dict: dict) -> None:
        """Handles the /start command to welcome the user."""
        user_id = user_command_dict["user_id"]

        welcome_message = (
            "<b>Welcome to the Bookkeeping Bot! 📊</b>\n\n"
            "I help you track your <i>income</i> and <i>expenses</i>. Just send me transaction details, "
            "e.g., <code>Spent 50 HKD on 7-11 today</code>, or use commands like <b>/help</b>, <b>/listcategories</b>, or <b>/summary</b>.\n\n"
            "If you're a first-time user, please use <b>/register</b> to set up your account.\n\n"
        )
        SendMessage(user_id, welcome_message)

    def help(self, user_command_dict: dict) -> None:
        """Handles the /help command to welcome the user."""
        user_id = user_command_dict["user_id"]

        help_message = (
            "<b>📖 How to Use the Bookkeeping Bot</b>\n\n"
            "<b>1. Record a transaction</b>: Send a message like <code>Spent 100 HKD on KFC</code> or <code>Received 1000 HKD salary</code>.\n"
            "<b>2. View categories</b>: Use <b>/listcategories</b> to see your income and expense categories.\n"
            "<b>3. Get a summary</b>: Use <b>/summary</b> to view your total income and expenses.\n"
            "<b>4. Need help?</b>: You're already here! Use <b>/help</b> anytime.\n\n"
            "<i>Note: Ensure your categories exist in the database. Contact support if you need assistance.</i>"
        )
        SendMessage(user_id, help_message)

    def transaction_parser_llm(self, user_command_dict: dict) -> None:
        """Handles the /ai command to parse transactions using LLM."""
        user_id = user_command_dict["user_id"]
        command = user_command_dict["command"]
        user_input = user_command_dict["user_input"]

        if command == user_input:
            guildline_message = (
                "<b><code>/ai</code>Command Guideline for Users</b>\n"
                "<b>Format:</b> <code>/ai [Income / Expense description]</code>\n"
                "<b>Example:</b> <code>/ai KFC 50</code>\n"
                "\n\n"
                "<b><code>/ai</code>指令使用指南</b>\n"
                "<b>格式：</b> <code>/ai [收入/消費 詳情]</code>\n"
                "<b>範例：</b> <code>/ai KFC 50</code>\n"
            )
            SendMessage(user_id, guildline_message)

            return Response(status=200)

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

            # Insert the transaction into the Supabase database
            # transaction_insert(transaction)

            # Format and send transaction_parse_result
            transaction_parse_result = (
                f"<b>⚙️ AI Transaction Parse Result:</b>\n\n"
                f"<b>User ID:</b> <code>{transaction['user_id']}</code>\n"
                f"<b>Date:</b> <code>{transaction['date']}</code>\n"
                f"<b>Category ID:</b> <code>{transaction['category_id']}</code>\n"
                f"<b>Category Type:</b> <code>{llm_response['category_type']}</code>\n"
                f"<b>Description:</b> <code>{transaction['description']}</code>\n"
                f"<b>Currency:</b> <code>{transaction['currency']}</code>\n"
                f"<b>Amount:</b> <code>{transaction['amount']}</code>"
            )

            keyboard_setting = {
                "inline_keyboard": [
                    [
                        {"text": "Change Date", "callback_data": "change_username"}
                    ],
                    [
                        {"text": "Change Category Type", "callback_data": "change_username"}
                    ],
                    [
                        {"text": "Change Description", "callback_data": "change_username"}
                    ],
                    [
                        {"text": "Change Currency", "callback_data": "change_username"}
                    ],
                    [
                        {"text": "Change Amount", "callback_data": "change_username"}
                    ]
                ]
            }
            SendInlineKeyboardMessage(user_id, transaction_parse_result, keyboard_setting)

    def register(self, user_command_dict: dict) -> None:
        """Handles the /register command to welcome the user."""
        user_id = user_command_dict["user_id"]

        settings_message = (
            f"<b>⚙️ Your Settings</b>\n\n"
            f"Username: {self.user_settings[user_id]["username"]}\n"
            f"Default Currency: {self.user_settings[user_id]["default_currency"]}\n\n"
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
        SendInlineKeyboardMessage(user_id, settings_message, keyboard_setting)

    def monthly_summary(self, user_command_dict: dict) -> None:
        """Handles the /monthlysummary command to welcome the user."""
        user_id = user_command_dict["user_id"]

        monthly_summary_message = (
            "<b>📅 Monthly Summary</b>\n\n"
            "This feature is under development. Stay tuned for updates!"
        )
        SendMessage(user_id, monthly_summary_message)