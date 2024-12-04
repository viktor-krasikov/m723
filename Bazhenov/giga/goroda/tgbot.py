import telebot
from dotenv import load_dotenv
import os
from gtts import gTTS
import speech_recognition as sr
import soundfile as sf
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
@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    chat_id = message.chat.id
    if chat_id in game_instance:
        voice_file = bot.get_file(message.voice.file_id)

        # Скачиваем аудиофайл
        downloaded_file = bot.download_file(voice_file.file_path)
        audio_file_path = 'D:\\temp\\audio_file.ogg'

        # Сохраняем загруженный файл во временное хранилище
        with open(audio_file_path, 'wb') as temp_audio:
            temp_audio.write(downloaded_file)

        # Читаем аудиофайл с помощью soundfile
        data, samplerate = sf.read(audio_file_path)

        # Записываем аудиофайл обратно в WAV формат
        sf.write("D:\\temp\\audio_file.wav", data, samplerate)

        # Преобразуем аудио в текст
        recognizer = sr.Recognizer()
        with sr.AudioFile("D:\\temp\\audio_file.wav") as source:
            audio_data = recognizer.record(source)
            try:
                # Используем Google Web Speech API для распознавания
                text = recognizer.recognize_google(audio_data, language='ru-RU')

                chat_id = message.chat.id
                if chat_id in game_instance:
                    response = game_instance.next(chat_id, text)
                    #bot.send_message(chat_id, response)
                    tts = gTTS(text=response, lang='ru')
                    tts.save(audio_file_path)  # Сохраняем аудио по тому же пути

                    with open(audio_file_path, 'rb') as audio_file:
                        bot.send_voice(chat_id, audio_file)

                else:
                    bot.send_message(chat_id, "Сначала начните игру")


                #bot.send_message(chat_id, f"Вы сказали: {text}")

                # Преобразуем текст обратно в аудио
                # tts = gTTS(text=text, lang='ru')
                # tts.save(audio_file_path)  # Сохраняем аудио по тому же пути
                #
                # response = game_instance.next(chat_id, text)
                # bot.send_message(chat_id, f"Бот сказал: {response}")
                # Преобразуем текст обратно в аудио


            except sr.UnknownValueError:
                bot.send_message(chat_id, "Не удалось распознать речь.")
            except sr.RequestError as e:
                bot.send_message(chat_id, f"Ошибка запроса к сервису распознавания: {e}")
    else:
        bot.send_message(chat_id, "Сначала начните игру")

    # Удаляем временный файл после использования
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)


if __name__ == '__main__':
    bot.polling(none_stop=True)
