from dotenv import load_dotenv
import os
import telebot
from goroda.goroda_game import GorodaGame

load_dotenv()
tg_token = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(tg_token)
goroda_game = GorodaGame()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Здравствуйте, сыграем в города?')

@bot.message_handler(func=lambda message: True)
def analyze(message):
    user_messages = {}
    user_id = message.chat.id
    res = goroda_game.town_game(message.text)
    bot.reply_to(message, res)

bot.polling(none_stop=True, interval=0)

