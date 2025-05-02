from openai import OpenAI
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
DEEPSEEK_API = os.getenv("DEEPSEEK_API")
TG_API = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

def ai_response(user_input):
    """Function to get AI response from Deepseek API."""
    client = OpenAI(api_key=DEEPSEEK_API, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{user_input}"},
        ],
        stream=False
    )

    return response.choices[0].message.content

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        ### Send message
        user_input = request.get_json()
        user_input_json = json.dumps(user_input, indent=4)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)