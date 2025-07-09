import yaml
import logging
import logging.config
from flask import Flask

def setup_logger():
    with open("logging_config.yml", 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

setup_logger()
app = Flask(__name__)
logger = logging.getLogger('flask_app')

@app.route('/')
def main():
  # showing different logging levels
  logger.debug("debug log info")
  logger.info("Info log information")
  logger.warning("Warning log info")
  logger.error("Error log info")
  logger.critical("Critical log info")
  return "testing logging levels."

if __name__ == '__main__':
  app.run(debug=True)
