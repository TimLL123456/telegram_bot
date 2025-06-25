from llm_tools import PerplexityLLM
from telegram_api import SendMessageToTelegram
from flask import Flask, Response, request


import os
from supabase import create_client
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

url= os.environ.get("SUPABASE_URL")
key= os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

app = Flask(__name__)

perplexity_llm = PerplexityLLM(model_name="sonar", temperature=0.0)

def _get_user_id(tg_user_input:str):
    """Retrieve the user ID from telegram chatroom api response."""
    return tg_user_input["message"]["from"]["id"]

def _get_category_id(cat_type:str, cat_name:str,  user_id:int):
    """Retrieve the category ID from the database based on category type, name, and user ID."""
    response = (
        supabase.table("categories")
        .select("category_id")
        .eq("category_type", cat_type)
        .eq("category_name", cat_name)
        .eq("user_id", user_id)
        .execute()
    )

    return response.data[0]["category_id"] if response.data else "Utilities"

@app.route('/', methods=['POST', "GET"])
def telegram():

    # Handle the incoming POST request from Telegram
    if request.method == 'POST':
        
        # Retrieve the user ID from telegram chatroom api response 
        user_input = request.get_json()

        # Extracts bookkeeping features by LLM
        llm_response = perplexity_llm.extract_bookkeeping_features(user_input["message"]["text"])

        user_id = _get_user_id(user_input)                                           # Retrieve the user ID from telegram chatroom api response
        category_id = _get_category_id("Expense", llm_response["category"], user_id) # Retrieve the category ID from supabase database

        print("-"* 50)
        print(f"LLM Response: {llm_response}")
        print(f"User ID: {user_id}, Category ID: {category_id}")

        if llm_response["is_transaction"]:
            transactions = {
                "user_id": user_id,
                "date": llm_response["date"],
                "category_id": category_id,
                "description": llm_response["description"],
                "currency": llm_response["currency"],
                "amount": llm_response["price"]
            }

            # print(f"Transactions to insert: {transactions}")

            # Insert the transaction into the Supabase database
            response = (
                supabase.table("transactions")
                .insert(transactions)
                .execute()
            )

        # Send the LLM response to Telegram
        SendMessageToTelegram(llm_response)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)