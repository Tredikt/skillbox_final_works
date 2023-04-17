from config_data.config import API_TOKEN, BOT_TOKEN
from telegram_bot import MyBot

if __name__ == "__main__":
    bot = MyBot(token=BOT_TOKEN, api_token=API_TOKEN)
    bot.run()
