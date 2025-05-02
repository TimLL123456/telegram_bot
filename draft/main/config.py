from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Config:
    ROOT_DIR = Path(os.path.dirname(__file__)).parent
    TG_BOT_API = os.getenv("TOKEN")
    DEEPSEEK_API = os.getenv("DEEPSEEK_API")