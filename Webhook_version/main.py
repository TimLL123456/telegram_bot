import asyncio
import json
import os
from dotenv import load_dotenv
import requests
from pprint import pprint
from flask import Flask, Response, request

### Get all the chatroom messages
# https://api.telegram.org/bot{TG_API}/getUpdates

### Send message from bot to chatroom
# https://api.telegram.org/bot{TG_API}/sendMessage?chat_id=1174923863&text=Hi%20How%20are%20you

### Setup webhook
# https://api.telegram.org/bot{TG_API}/setWebhook?url={serveo.net url}

### Telegram API URL Parameters
# https://core.telegram.org/bots/api#sendmessage

load_dotenv()
CMC_API = os.getenv("COINMARKETCAP_API")
TG_API = os.getenv("TOKEN")

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        ### Send message
        user_input = request.get_json()
        user_input_json = json.dumps(user_input, indent=4)

        message = "How are you"

        url = f"https://api.telegram.org/bot{TG_API}/sendMessage"

        params = {
            "chat_id": 1174923863,
            "text": message,
        }

        ### Set command
        # commands = [
        #     {"command": "start", "description": "Start the bot"},
        #     {"command": "help", "description": "Get help"}
        # ]

        # Telegram API URL for setMyCommands
        # url = f"https://api.telegram.org/bot{TG_API}/setMyCommands"

        # Parameters for the API request (serialize commands to JSON)
        # data = {
        #     "commands": json.dumps(commands)
        # }

        # Send the request to Telegram API
        response = requests.post(url, data=params)


        return Response("ok", status=200)

    return "<h1>Hello, World!</h1>"

async def main(crypto):

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {
        "symbol": crypto,
        "convert": "USD"
    }
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API,
    }

    response = requests.get(
        url,
        headers=headers,
        params=parameters
    ).json()

    # pprint(response)
    asset_price = response["data"]["BTC"]["quote"]["USD"]["price"]

    print(f"BTC price: {asset_price}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)