from money_manager_bot import MoneyManagerBot
from config import Config
import logging

def log_config():
    ### Set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Set the logging level to INFO

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler("./telegram_bot/system_log.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create a console handler to print logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def main():
    logger = log_config()

    try:
        logger.info("Initializing Money Manager Bot ...")
        bot = MoneyManagerBot(Config.TG_BOT_API, Config.DEEPSEEK_API)
        bot.initialize()

        logger.info("Starting Money Manager Bot ...")
        bot.run()

    except Exception as e:
        logger.error(f"Application failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()