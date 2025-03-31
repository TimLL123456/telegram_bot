from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from aiohttp import web
import os
import threading

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [KeyboardButton("Open Web App", web_app=WebAppInfo("http://localhost:8000/web_app.html"))]
    ]
    await update.message.reply_text(
        "Welcome! Click the button below to open the Web App.",
        reply_markup=ReplyKeyboardMarkup(kb)
    )

def run_http_server():
    async def handler(request):
        return web.FileResponse(os.path.join(os.path.dirname(__file__), "web_app.html"))

    app = web.Application()
    app.router.add_get('/', handler)
    app.router.add_static('/', path=os.path.dirname(__file__))

    web.run_app(app, host='localhost', port=8000)

async def main():
    # Start HTTP server in a separate thread
    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()
    print("HTTP server running at http://localhost:8000")

    # Start Telegram bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())