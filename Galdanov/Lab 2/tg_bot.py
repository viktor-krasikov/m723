from dotenv import load_dotenv
import os
import telebot
import re
from goroda.goroda_game import GorodaGame

load_dotenv()
tg_token = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(tg_token)
goroda_game = GorodaGame()

def giveupchecker(message):
    message = message.lower()
    pattern = r'\b(я\s*сдаюсь|сдаюсь|сдамся|сдаюсь|сдатьс|сдаюс\s*я)\b'
    if re.search(pattern, message):
        return True
    else:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Здравствуйте, сыграем в города?')

@bot.message_handler(func=lambda message: True)
def analyze(message):
    user_id = message.chat.id
    if giveupchecker(message.text) is False:
        res = goroda_game.town_game(message.text)
    else:
        res = "Хорошо, давайте начнем снова"
    bot.reply_to(message, res)

bot.polling(none_stop=True, interval=0)

