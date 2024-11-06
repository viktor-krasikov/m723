# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from dotenv import load_dotenv
import os
import threading

# Загрузка переменных среды
load_dotenv()
TOKEN = os.getenv('TOKEN')
GIGATOKEN = os.getenv('GIGATOKEN')

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=GIGATOKEN, verify_ssl_certs=False)

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения истории игры для каждого пользователя
user_histories = {}
user_timers = {}
user_played_cities = {}
city_info = {}  # Словарь для хранения последней информации о городе

default_messages = [
    SystemMessage(
        content="Ты играешь в города. Каждый участник называет реально существующий город. Название города должно начинаться на букву, которой оканчивается название предыдущего города, за исключением 'ь' и 'ъ'.")
]

def extract_last_letter(city):
    last_letter = city.strip()[-1]
    return last_letter if last_letter not in "ьъ" else city.strip()[-2]

# Функция для нормализации названия города (удаление окончаний)
def normalize_city_name(city):
    city = city.lower().strip()
    endings = ["ий", "ый", "ой", "ая", "яя", "ое", "ье", "ое", "а", "я", "ъ", "ь"]
    for ending in endings:
        if city.endswith(ending):
            return city[:-len(ending)]
    return city

# Проверка, был ли город уже назван (с нормализацией названий)
def is_city_used(city, played_cities):
    normalized_city = normalize_city_name(city)
    first_letter = normalized_city[0].lower()
    return any(normalized_city == normalize_city_name(c) for c in played_cities if normalize_city_name(c)[0].lower() == first_letter)

def start_timer(chat_id, timeout=60):
    if chat_id in user_timers:
        user_timers[chat_id].cancel()
    timer = threading.Timer(timeout, handle_time_out, [chat_id])
    user_timers[chat_id] = timer
    timer.start()


def handle_time_out(chat_id):
    bot.send_message(chat_id, "Время на ход вышло! Вы проиграли.")
    reset_game(chat_id)

def reset_game(chat_id):
    user_histories[chat_id] = default_messages.copy()
    user_played_cities[chat_id] = []
    city_info[chat_id] = None

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    reset_game(chat_id)
    bot.send_message(chat_id, "Начнём игру в города! Назовите первый город.")
    start_timer(chat_id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_input = message.text.strip().capitalize()

    if chat_id not in user_played_cities:
        user_played_cities[chat_id] = []
    if chat_id not in user_histories:
        user_histories[chat_id] = default_messages.copy()

    # Проверка, что город уже использован
    if is_city_used(user_input, user_played_cities[chat_id]):
        bot.send_message(chat_id, "Такой город уже был. Назовите другой.")
        return

    # Проверка на первую букву города
    if user_played_cities[chat_id]:
        last_letter = extract_last_letter(user_played_cities[chat_id][-1])
        if user_input[0].lower() != last_letter:
            bot.send_message(chat_id, f"Вы должны назвать город на букву '{last_letter.upper()}'")
            return

    # Проверка существования города
    verification_response = chat.invoke([HumanMessage(content=f"Существует ли город с названием {user_input}?")])
    if "нет" in verification_response.content.lower() or "не существует" in verification_response.content.lower():
        bot.send_message(chat_id, f"Город '{user_input}' не найден. Пожалуйста, введите другой город.")
        return

    # Если город существует, продолжаем игру
    user_played_cities[chat_id].append(user_input)
    start_timer(chat_id)

    # Формируем запрос для GigaChat для следующего города
    user_histories[chat_id].append(
        HumanMessage(content=f"Назови город на букву '{extract_last_letter(user_input).upper()}'"))
    response = chat.invoke(user_histories[chat_id])

    print('user id -', message.chat.id)
    print('human -', HumanMessage(content=user_input).content)
    print('bot -', response.content)
    print('history')
    for key, value in user_histories.items():
        print('  id -', key)
        for i in value:
            print("    ", type(i), i.content)
    # Проверка победы или продолжение
    if response.content.lower() in (c.lower() for c in user_played_cities[chat_id]):
        bot.send_message(chat_id, "Поздравляю! Вы победили, все возможные города были использованы.")
        reset_game(chat_id)
    else:
        user_played_cities[chat_id].append(response.content)
        user_histories[chat_id].append(response)
        city_info[chat_id] = response.content  # Сохраняем информацию для кнопки «Подробнее»

        # Создаем клавиатуру с кнопкой «Подробнее»
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Подробнее", callback_data="more_info"))
        bot.send_message(chat_id, response.content, reply_markup=markup)

# Обработчик для кнопки "Подробнее"
@bot.callback_query_handler(func=lambda call: call.data == "more_info")
def callback_more_info(call):
    chat_id = call.message.chat.id
    if chat_id in city_info and city_info[chat_id]:
        # Запрашиваем у GigaChat подробную информацию о последнем городе
        detailed_response = chat.invoke([HumanMessage(content=f"Расскажи подробнее о городе {city_info[chat_id]}.")])
        bot.send_message(chat_id, detailed_response.content)
    else:
        bot.send_message(chat_id, "Нет данных для показа. Попробуйте снова после следующего хода.")

if __name__ == '__main__':
    bot.polling(none_stop=True)



# import telebot
# from langchain.schema import HumanMessage, SystemMessage
# from langchain_community.chat_models.gigachat import GigaChat
# from dotenv import load_dotenv
# import os
#
# # Загрузка переменных среды
# load_dotenv()
# TOKEN = os.getenv('TOKEN')
# GIGATOKEN = os.getenv('GIGATOKEN')
#
# # Авторизация в сервисе GigaChat
# chat = GigaChat(credentials=GIGATOKEN, verify_ssl_certs=False)
#
# # Инициализация бота
# bot = telebot.TeleBot(TOKEN)
#
# # Словарь для хранения историй пользователей
# user_histories = {}
#
# # Список для хранения истории игры
# history_game = []
# # Создание сообщения для контекста
# default_messages = [
#     SystemMessage(
#         content="Ты игрок в города. Города это игра, в которой каждый участник в свою очередь называет реально существующий в данный момент времени город любой существующей страны, название которого начинается на ту букву, которой оканчивается название предыдущего города, без каких-либо исключений. Исключением в правилах игры являются названия, оканчивающиеся на «ь» (мягкий знак) и «ъ» (твёрдый знак): в таких случаях участник называет город на предпоследнюю букву.")
# ]
#
#
# def extract_letters(s):
#     if len(s) < 2:
#         return "String too short"
#     last_letter = s[-1]
#     if last_letter in "ъь":
#         last_letter = s[-2]
#     return last_letter
#
# def find_city(s):
#     string_history_game = [city for city in history_game if city[0] == s]
#     return string_history_game
#
# # Обработчик команды /start
# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, "Привет! Нужна шутка?")
#     # Инициализация истории для нового пользователя
#     user_histories[message.chat.id] = default_messages.copy()
#
#
# # Обработчик текстовых сообщений
# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
#     user_input = message.text
#     if user_input in history_game:
#         bot.send_message(message.chat.id, 'Это слово есть')
#         return
#
#     # Получаем историю сообщений для текущего пользователя
#     if message.chat.id not in user_histories:
#         user_histories[message.chat.id] = default_messages.copy()
#
#     history_game.append(user_input)
#     lastw = extract_letters(user_input)
#     print(lastw)
#     scity = find_city(lastw)
#     print(scity)
#     # Добавляем сообщение пользователя в контекст
#     user_histories[message.chat.id].append(
#         HumanMessage(
#             content='Напиши один город на букву ' + lastw + '. ' + 'Список, который нельзя называть: ' + ', '.join(scity) + '.'
#         )
#     )
#
#     print(user_histories[message.chat.id])
#
#     # Отправляем все сообщения в GigaChat для обработки
#     res = chat.invoke(user_histories[message.chat.id])
#     history_game.append(res.content)
#
#     # Добавляем ответ GigaChat в контекст
#     user_histories[message.chat.id].append(res)
#
#     print('user id -', message.chat.id)
#     print('human -', HumanMessage(content=user_input).content)
#     print('bot -', res.content)
#     print('history')
#     for key, value in user_histories.items():
#         print('  id -', key)
#         for i in value:
#             print("    ", type(i), i.content)
#
#     # Отправляем ответ пользователю
#     bot.send_message(message.chat.id, res.content)
#
#
# # Главная функция для запуска бота
# if __name__ == '__main__':
#     bot.polling(none_stop=True)