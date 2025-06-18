from llm_tools import PerplexityLLM
from telegram_api import SendMessageToTelegram
from flask import Flask, Response, request

app = Flask(__name__)

perplexity_llm = PerplexityLLM(model_name="sonar", temperature=0.0)

@app.route('/', methods=['POST', "GET"])
def telegram():

    if request.method == 'POST':
        # Handle the incoming POST request from Telegram
        user_input = request.get_json()
        print(f"User input: {user_input}")

        llm_response = perplexity_llm.extract_bookkeeping_features(user_input["message"]["text"])
        SendMessageToTelegram(llm_response)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)