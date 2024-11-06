import telebot
from dotenv import load_dotenv
import os
from gorodagame import GorodaGame

# Загрузка переменных среды
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Инициализация бота и игры
bot = telebot.TeleBot(TOKEN)
game_instance = GorodaGame()


@bot.message_handler(commands=['start'])
def start(message):
    stg = game_instance.start_game(message.chat.id)
    bot.send_message(message.chat.id, stg)


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    res = game_instance.next(message)
    print("res=" + res)
    bot.send_message(message.chat.id, res)


if __name__ == '__main__':
    bot.polling(none_stop=True)
