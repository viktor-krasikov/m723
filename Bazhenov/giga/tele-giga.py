# -*- coding: utf-8 -*-
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

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения историй пользователей
user_histories = {}

# Список для хранения истории игры
history_game = []
# Создание сообщения для контекста
default_messages = [
    SystemMessage(
        content="Ты игрок в города. Города это игра, в которой каждый участник в свою очередь называет реально существующий в данный момент времени город любой существующей страны, название которого начинается на ту букву, которой оканчивается название предыдущего города, без каких-либо исключений. Исключением в правилах игры являются названия, оканчивающиеся на «ь» (мягкий знак) и «ъ» (твёрдый знак): в таких случаях участник называет город на предпоследнюю букву.")
]


def extract_letters(s):
    if len(s) < 2:
        return "String too short"
    last_letter = s[-1]
    if last_letter in "ъь":
        last_letter = s[-2]
    return last_letter

def find_city(s):
    string_history_game = [city for city in history_game if city[0] == s]
    return string_history_game

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Нужна шутка?")
    # Инициализация истории для нового пользователя
    user_histories[message.chat.id] = default_messages.copy()


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    if user_input in history_game:
        bot.send_message(message.chat.id, 'Это слово есть')
        return

    # Получаем историю сообщений для текущего пользователя
    if message.chat.id not in user_histories:
        user_histories[message.chat.id] = default_messages.copy()

    history_game.append(user_input)
    lastw = extract_letters(user_input)
    print(lastw)
    scity = find_city(lastw)
    print(scity)
    # Добавляем сообщение пользователя в контекст
    user_histories[message.chat.id].append(HumanMessage(content='Напиши один город на букву ' + lastw + '. ' +
                                                                'Список, который нельзя называть: ' + ', '.join(
        scity) + '.'))

    print(user_histories[message.chat.id])

    # Отправляем все сообщения в GigaChat для обработки
    res = chat.invoke(user_histories[message.chat.id])
    history_game.append(res.content)

    # Добавляем ответ GigaChat в контекст
    user_histories[message.chat.id].append(res)

    print('user id -', message.chat.id)
    print('human -', HumanMessage(content=user_input).content)
    print('bot -', res.content)
    print('history')
    for key, value in user_histories.items():
        print('  id -', key)
        for i in value:
            print("    ", type(i), i.content)

    # Отправляем ответ пользователю
    bot.send_message(message.chat.id, res.content)


# Главная функция для запуска бота
if __name__ == '__main__':
    bot.polling(none_stop=True)