import json
import os
from dotenv import load_dotenv
import requests
from pprint import pprint
from flask import Flask, Response, request

from typing import Optional
from langchain_perplexity import ChatPerplexity
from langchain_core.prompts import ChatPromptTemplate
from datetime import date
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
PERPLEXITY_API = os.getenv("PERPLEXITY_API")
TG_API = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert bookkeeping assistant, fluent in both English and Cantonese. Your task is to extract transaction details from the user's message.

            **Rules & Context:**
            - The current date is {current_date} in ISO format (e.g., 2025-05-02).
            - The currency is always HKD.
            - If the message is a transaction, set 'is_transaction' to True.
            - If the message is NOT a transaction (like a greeting), set 'is_transaction' to False and other fields to null.
            - **Local Context:** '三哥' or '譚仔' refers to the restaurant 'TamJai SamGor'.
            
            **Examples of how to parse transactions:**

            ---
            **User Input:** 琴日三哥46
            **Your Output:**
            {{
                "is_transaction": true,
                "date": "2025-06-16",  // Assuming today is 2025-06-17
                "category": "Food",
                "description": "三哥 (TamJai SamGor)",
                "price": 46.0
            }}
            ---
            **User Input:** Lunch at Pret 85 dollars
            **Your Output:**
            {{
                "is_transaction": true,
                "date": "{current_date}",
                "category": "Food",
                "description": "Lunch at Pret",
                "price": 85.0
            }}
            ---
            **User Input:** 上星期五睇戲 120蚊
            **Your Output:**
            {{
                "is_transaction": true,
                "date": "2025-06-13", // Assuming today is 2025-06-17
                "category": "Entertainment",
                "description": "睇戲",
                "price": 120.0
            }}
            ---
            **User Input:** Hi there
            **Your Output:**
            {{
                "is_transaction": false,
                "date": null,
                "category": null,
                "description": null,
                "price": null
            }}
            ---
            """,
        ),
        ("human", "{user_message}"),
    ]
)


os.environ["PPLX_API_KEY"] = PERPLEXITY_API
# llm = init_chat_model("sonar", model_provider="perplexity")
llm = ChatPerplexity(model="sonar", temperature=0.0)

app = Flask(__name__)

class FeaturesFormatter(BaseModel):
    """Feature formatter to extract features from user text. If the text is not a transaction, set is_transaction to False."""

    is_transaction: bool = Field(description="Set to True if the text describes a financial transaction, otherwise set to False.")
    date: Optional[str] = Field(description="Date of the transaction in ISO format (e.g., 2025-05-02). Should be null if not a transaction.")
    category: Optional[str] = Field(description="Category of the transaction (e.g., Food, Transport, Shopping). Should be null if not a transaction.")
    description: Optional[str] = Field(description="A concise summary of the transaction. Should be null if not a transaction.")
    price: Optional[float] = Field(description="Price of the transaction (must be a number). Should be null if not a transaction.")

# Function to extract features from user input text
# def extract_bookkeeping_features(text: str) -> dict:
#     # Initialize the LLM with structured output
#     structured_llm = llm.with_structured_output(FeaturesFormatter)
#     structured_output = structured_llm.invoke(text)
#     return structured_output.model_dump()

def extract_bookkeeping_features(text: str) -> dict:
    """
    Extracts bookkeeping features using a robust prompt and structured output.
    """
    # 1. Chain the prompt with the LLM and the structured output parser
    structured_llm = llm.with_structured_output(FeaturesFormatter)
    chain = prompt | structured_llm

    # 2. Invoke the chain with the user message and current date
    response_model = chain.invoke({
        "user_message": text,
        "current_date": date.today().isoformat()
    })
    
    # 3. Return the model's output as a dictionary
    return response_model.model_dump()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        ### Send message
        user_input = request.get_json()
        user_input_json = json.dumps(user_input, indent=4)

        print(f"User input: {user_input_json}")

        ai_response = extract_bookkeeping_features(user_input["message"]["text"])

        print(ai_response)

        if ai_response.get("is_transaction"):
            # It's a valid transaction, format and send it
            ai_response_text = (
                f"Transaction Logged:\n"
                f"Date: {ai_response['date']}\n"
                f"Category: {ai_response['category']}\n"
                f"Description: {ai_response['description']}\n"
                f"Price: HKD {ai_response['price']}"
            )
        else:
            # It's not a transaction, send a different message
            ai_response_text = "I'm ready to log your expenses! Just tell me what you bought."

        print(f"AI response: {ai_response_text}")

        url = f"https://api.telegram.org/bot{TG_API}/sendMessage"

        params = {
            "chat_id": 1174923863,
            "text": str(ai_response)
        }

        response = requests.post(url, data=params)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)