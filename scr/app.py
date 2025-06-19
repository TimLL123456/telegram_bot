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

def _get_cat_id(cat_type:str, cat_name:str):

    response = (
        supabase.table("categories")
        .select("category_id")
        .eq("category_type", cat_type)
        .eq("category_name", cat_name)
        .eq("user_id", 444555666)
        .execute()
    )

    return response.data[0]["category_id"] if response.data else "Utilities"

@app.route('/', methods=['POST', "GET"])
def telegram():

    if request.method == 'POST':
        # Handle the incoming POST request from Telegram
        user_input = request.get_json()
        llm_response = perplexity_llm.extract_bookkeeping_features(user_input["message"]["text"])

        if llm_response["is_transaction"]:
            transactions = {
                "user_id": 444555666,
                "date": llm_response["date"],
                "category_id": _get_cat_id("Expense", llm_response["category"]),
                "description": llm_response["description"],
                "currency": llm_response["currency"],
                "amount": llm_response["price"]
            }

            # print(f"Transactions to insert: {transactions}")

            response = (
                supabase.table("transactions")
                .insert(transactions)
                .execute()
            )

        SendMessageToTelegram(llm_response)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)