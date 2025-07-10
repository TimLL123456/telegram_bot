from config import Config
from custom_logger import *

import logging
from flask_ngrok import run_with_ngrok
from flask import Flask, jsonify, request

app = Flask(__name__)
run_with_ngrok(app)  # Starts ngrok when app runs

# Set Logger
logger = logger_setup(logger_name="app", logger_filename="app.log")
logger = logging.getLogger("app.main")


@app.route('/', methods=['GET'])
@log_function(logger)
def main():

    config = Config()

    logger.info("Telegram Bot Running")
    data = {"message": "Hello World"}
    return jsonify(data)
  

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        logger.error(e)