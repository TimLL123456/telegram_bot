from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TG_BOT_API = os.getenv("TOKEN")
    DEEPSEEK_API = os.getenv("DEEPSEEK_API")
