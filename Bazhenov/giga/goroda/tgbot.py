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
    def on_time_is_up(chat_id):
        print(f"Выполнение on_time_is_up ({chat_id})")
        bot.send_message(chat_id, "Время на ход вышло! Вы проиграли.")
        game_instance.stop_game(chat_id)

    stg = game_instance.start_game(message.chat.id, on_time_is_up)
    bot.send_message(message.chat.id, stg)


@bot.message_handler(func=lambda message: message.text.lower() == "сдаюсь")
def sdayus(message):
    chat_id = message.chat.id
    if chat_id in game_instance:
        bot.send_message(chat_id, "Я победил!")
        game_instance.stop_game(chat_id)
    else:
        bot.send_message(chat_id, "Сначала начните игру")

@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    chat_id = message.chat.id
    if chat_id in game_instance:
        user_input = message.text.strip()
        response = game_instance.next(chat_id, user_input)
        bot.send_message(chat_id, response)
    else:
        bot.send_message(chat_id, "Сначала начните игру")


if __name__ == '__main__':
    bot.polling(none_stop=True)
