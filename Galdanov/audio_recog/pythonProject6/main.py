import telebot
import speech_recognition as sr
import os
import soundfile as sf
from gtts import gTTS

# Инициализация Telegram-бота
API_TOKEN = 'Temp'  # Замените на свой токен
bot = telebot.TeleBot(API_TOKEN)


# Функция для преобразования аудио в текст с использованием Sphinx
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()

    # Загружаем аудиофайл с использованием soundfile
    audio_data, samplerate = sf.read(audio_file)

    # Преобразуем данные в объект AudioData для SpeechRecognition
    with open('temp_audio.wav', 'wb') as f:
        sf.write(f, audio_data, samplerate)

    # Применяем SpeechRecognition для распознавания речи с использованием Sphinx
    with sr.AudioFile('temp_audio.wav') as source:
        audio = recognizer.record(source)

        try:

            text = recognizer.recognize_google(audio, language='ru-RU')
            return text
        except sr.UnknownValueError:
            return "Не удалось распознать речь."
        except sr.RequestError as e:
            return f"Ошибка при обработке запроса: {e}"

def text_to_speech(text, lang='ru'):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_file = 'tts_output.mp3'
    tts.save(audio_file)  # Сохраняем аудио-файл
    return audio_file


# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне аудио, и я преобразую его в текст.")


# Обработка аудио сообщений
@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    try:
        # Получаем информацию о файле
        file_info = bot.get_file(message.voice.file_id)

        # Путь, по которому будет загружен файл
        file_path = file_info.file_path

        # Путь для сохранения аудиофайла
        audio_file = 'received_audio.ogg'

        # Загружаем аудиофайл с Telegram
        downloaded_file = bot.download_file(file_path)

        # Сохраняем файл локально
        with open(audio_file, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Преобразуем аудио в текст
        text = audio_to_text(audio_file)

        # Отправляем результат обратно пользователю
        bot.reply_to(message, f"Распознанный текст: {text}")

        # Преобразуем текст обратно в речь (TTS) и отправляем пользователю
        if not text == "Не удалось распознать речь.":
            tts_audio_file = text_to_speech(text)

        # Отправляем аудиофайл пользователю
        if tts_audio_file:
            # Отправляем аудиофайл пользователю
            with open(tts_audio_file, 'rb') as audio:
                bot.send_voice(message.chat.id, audio)

            # Удаляем временные файлы
            os.remove(tts_audio_file)
        else:
            bot.reply_to(message, "Произошла ошибка при преобразовании текста в речь.")

        # Удаляем временные файлы
        os.remove(audio_file)
        os.remove('temp_audio.wav')

    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке аудио: {e}")


# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
