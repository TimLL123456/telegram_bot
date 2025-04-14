import asyncio
import os
from dotenv import load_dotenv
import requests
from pprint import pprint
from flask import Flask, Response, request

### Get all the chatroom messages
# https://api.telegram.org/bot{TG_API}/getUpdates

### Send
# https://api.telegram.org/bot{TG_API}/sendMessage?chat_id=1174923863&text=Hi%20How%20are%20you

### 
# https://api.telegram.org/bot{TG_API}/setWebhook?url={serveo.net url}

load_dotenv()
CMC_API = os.getenv("COINMARKETCAP_API")
TG_API = os.getenv("TOKEN")

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
           
        # requests.post("https://api.telegram.org/bot7879762613:AAFLGGOSyXpaGJWWnzTjt7A6lz0JYX4p7EY/sendMessage?chat_id=1174923863&text=Hi%20How%20are%20you")
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
    
    