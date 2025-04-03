from telegram import BotCommand
from telegram.ext import Application
from config import Config
from handler import setup_handlers

# print(Config.TG_BOT_API, Config.DEEPSEEK_API)

class MoneyManagerBot:

    COMMANDS = [
        BotCommand("start", "Start the bot and greeting"),
        BotCommand("menu", "Show the operation menu")
    ]

    def __init__(self, tg_bot_api, deepseek_api):
        self.app = Application.builder().token(tg_bot_api).post_init(self._setup_commands).build()

    async def _setup_commands(self, application):
        await application.bot.set_my_commands(self.COMMANDS)

    def initialize(self):
        setup_handlers(self.app)

    def run(self):
        self.app.run_polling()

if __name__ == "__main__":
      bot = MoneyManagerBot(Config.TG_BOT_API, Config.DEEPSEEK_API)
      bot.initialize()
      bot.run()