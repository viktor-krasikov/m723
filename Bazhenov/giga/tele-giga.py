import telebot
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from dotenv import load_dotenv
import os

# Загрузка переменных среды
load_dotenv()
TOKEN = os.getenv('TOKEN')
GIGATOKEN = os.getenv('GIGATOKEN')

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=GIGATOKEN, verify_ssl_certs=False)

# Создание списка сообщений для контекста
messages = [
    SystemMessage(content="Ты шутник, который шутит над каждым сообщением собеседника.")
]

# Инициализация бота
bot = telebot.TeleBot(TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Нужна шутка?")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    messages.append(HumanMessage(content=user_input))  # Добавляем сообщение пользователя в контекст
    res = chat.invoke(messages)  # Отправляем все сообщения в GigaChat для обработки
    messages.append(res)  # Добавляем ответ GigaChat в контекст

    print('human -', HumanMessage(content=user_input).content)
    print('bot -', res.content)

    # Отправляем ответ пользователю
    bot.send_message(message.chat.id, res.content)


# Главная функция для запуска бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
