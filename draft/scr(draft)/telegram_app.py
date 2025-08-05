from config import Config
from custom_logger import *

import logging
from flask import Flask, jsonify, request

app = Flask(__name__)

# Set Logger
logger = logger_setup(logger_name="app", logger_filename="app.log")
logger = logging.getLogger("app.main")


# @app.route('/', methods=['GET'])
# @log_function(logger)

  

# if __name__ == "__main__":
#     app.run(debug=True)