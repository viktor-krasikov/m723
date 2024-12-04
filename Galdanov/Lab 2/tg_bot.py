from dotenv import load_dotenv
import os
import telebot
import re
from goroda.goroda_game import GorodaGame

load_dotenv()
tg_token = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(tg_token)
goroda_game = GorodaGame()

#TODO: Сделать скачивание аудиофайла с тш
#TODO: Сделать конвертацию и анализ
#TODO: Сделать удаление

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    # Получаем объект аудиофайла
    audio_file = message.audio
    file_id = audio_file.file_id  # ID файла, который будет использован для скачивания
    file_info = bot.get_file(file_id)  # Получаем информацию о файле
    file_path = file_info.file_path  # Путь к файлу в системе Telegram

    # Скачиваем файл
    downloaded_file = bot.download_file(file_path)
    print("Скачал аудиозапись")

    # Сохраняем аудиофайл на диск
    with open('audio.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Здравствуйте, сыграем в города?')

@bot.message_handler(func=lambda message: True)
def analyze(message):
    user_id = message.chat.id
    res = goroda_game.town_game(message.text)
    bot.reply_to(message, res)

bot.polling(none_stop=True, interval=0)

