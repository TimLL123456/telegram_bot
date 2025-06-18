import config
import requests

def SendMessageToTelegram(llm_response:dict) -> None:
    """
    Sends a message to a Telegram chat using the bot API.
    
    Args:
        llm_response (dict): The response from the LLM containing the message to send.
    """

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

    params = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": str(llm_response)
    }

    requests.post(url, data=params)