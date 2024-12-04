import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import config
from goroda_game import GorodaGame

bot_token = config.TELEGRAM_BOT_TOKEN
bot = telebot.TeleBot(bot_token)
game = GorodaGame()

# Создание клавиатуры с кнопками
def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = KeyboardButton("Старт")
    stop_button = KeyboardButton("Стоп")
    keyboard.add(start_button, stop_button)
    return keyboard


@bot.message_handler(commands=["start"])
def start_command(message):
    """Обрабатывает команду /start."""
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "Добро пожаловать в игру 'Города'! Нажмите 'Старт', чтобы начать игру.",
        reply_markup=create_main_keyboard()
    )


@bot.message_handler(func=lambda message: message.text == "Старт")
def start_game(message):
    """Обрабатывает нажатие кнопки 'Старт'."""
    user_id = message.chat.id
    response = game.start(user_id)
    bot.send_message(user_id, response, reply_markup=create_main_keyboard())


@bot.message_handler(func=lambda message: message.text == "Стоп")
def stop_game(message):
    """Обрабатывает нажатие кнопки 'Стоп'."""
    user_id = message.chat.id
    response = game.stop(user_id)
    bot.send_message(user_id, response, reply_markup=create_main_keyboard())


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обрабатывает текстовые сообщения."""
    user_id = message.chat.id
    user_input = message.text.strip()
    response = game.next(user_id, user_input)
    bot.send_message(user_id, response, reply_markup=create_main_keyboard())


if __name__ == "__main__":
    bot.polling(none_stop=True)
