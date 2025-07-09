import os
import logging
from dotenv import load_dotenv

class Config:
    def __init__(self):

        # Load environment variables from a .env file
        load_dotenv()

        # 1. Define all required environment variable keys and their values in a dictionary.
        #    This makes them easy to check in a loop.
        required_vars = {
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
            "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
            "SUPABASE_URL": os.getenv("SUPABASE_URL"),
            "SUPABASE_KEY": os.getenv("SUPABASE_KEY")
        }

        # 2. Use a list comprehension to find all keys whose values are None or empty.
        #    This logic is inspired by the provided search result [1].
        missing_vars = [key for key, value in required_vars.items() if not value]

        # 3. If the list of missing variables is not empty, raise a specific error.
        if missing_vars:
            # The error message now lists exactly which variables to check in your .env file.
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # If the check passes, you can assign the variables for use in your app
        self.DEEPSEEK_API_KEY = required_vars["DEEPSEEK_API_KEY"]
        self.PERPLEXITY_API_KEY = required_vars["PERPLEXITY_API_KEY"]
        self.TELEGRAM_BOT_TOKEN = required_vars["TELEGRAM_BOT_TOKEN"]
        self.SUPABASE_URL = required_vars["SUPABASE_URL"]
        self.SUPABASE_KEY = required_vars["SUPABASE_KEY"]

        # Configure logging
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Sets up a logger with file and console handlers."""
        logger = logging.getLogger('bookkeeping_bot')
        logger.setLevel(logging.debug)

        # File handler
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(module)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger