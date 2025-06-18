from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import requests
from pprint import pprint
from flask import Flask, Response, request

from typing import Optional
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

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

os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API
llm = init_chat_model("deepseek-chat", model_provider="deepseek")
llm = init_chat_model("sonar", model_provider="perplexity")

app = Flask(__name__)

class FeaturesFormatter(BaseModel):
    """Feature formatter to extract features from user text. If the text is not a transaction, set is_transaction to False."""

    is_transaction: bool = Field(description="Set to True if the text describes a financial transaction, otherwise set to False.")
    date: Optional[str] = Field(description="Date of the transaction in ISO format (e.g., 2025-05-02). Should be null if not a transaction.")
    category: Optional[str] = Field(description="Category of the transaction (e.g., Food, Transport, Shopping). Should be null if not a transaction.")
    description: Optional[str] = Field(description="A concise summary of the transaction. Should be null if not a transaction.")
    price: Optional[float] = Field(description="Price of the transaction in HKD. Should be null if not a transaction.")

# Function to extract features from user input text
def extract_bookkeeping_features(text: str) -> dict:
    # Initialize the LLM with structured output
    structured_llm = llm.with_structured_output(FeaturesFormatter)
    structured_output = structured_llm.invoke(text)
    return structured_output.model_dump()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        ### Send message
        user_input = request.get_json()
        user_input_json = json.dumps(user_input, indent=4)

        print(f"User input: {user_input_json}")

        ai_response = extract_bookkeeping_features(user_input["message"]["text"])

        print(f"AI response: {ai_response}")

        url = f"https://api.telegram.org/bot{TG_API}/sendMessage"

        params = {
            "chat_id": 1174923863,
            "text": str(ai_response)
        }

        response = requests.post(url, data=params)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)