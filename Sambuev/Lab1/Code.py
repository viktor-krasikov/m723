# import pymorphy2
#
# morph = pymorphy2.MorphAnalyzer()
# a = input()
# b = morph.parse(a)[0]
# b = b.tag.cyr_repr
# print(b)
#7523952838:AAFNj64tq3LW0PB80PStDC7mC1dwuG0-F6g

import telebot
import pymorphy2
from pymystem3 import Mystem
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import re

# Инициализация морфологических анализаторов
morph = pymorphy2.MorphAnalyzer()
mystem = Mystem()

# Укажите ваш токен, который вы получили от BotFather
TOKEN = '7523952838:AAFNj64tq3LW0PB80PStDC7mC1dwuG0-F6g'
bot = telebot.TeleBot(TOKEN)

# Переменная для хранения текущего анализатора (по умолчанию оба)
current_analyzer = 'both'


# Функция для морфологического анализа с использованием pymorphy2
def analyze_with_pymorphy2(text):
    parsed_words = morph.parse(text)
    interpretations = []

    for i, parsed_word in enumerate(parsed_words, 1):
        interpretations.append(f"Вариант {i}: {parsed_word.tag.cyr_repr}")

    return '\n'.join(interpretations)


# Обновленная функция для морфологического анализа с использованием pymystem3
def analyze_with_mystem(text):
    analysis = mystem.analyze(text)
    results = []

    for word in analysis:
        if 'analysis' in word and word['analysis']:
            for i, interpretation in enumerate(word['analysis'], 1):
                results.append(f"Вариант {i}: {interpretation['gr']}")

    return '\n'.join(results) if results else "Анализ не найден"


# Функция для создания клавиатуры с кнопками
def create_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_pymorphy2 = KeyboardButton('Использовать pymorphy2')
    button_mystem = KeyboardButton('Использовать mystem')
    button_both = KeyboardButton('Использовать оба анализатора')
    keyboard.add(button_pymorphy2, button_mystem, button_both)
    return keyboard


# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Привет! Отправь мне любое слово или предложение, и я сделаю его морфологический разбор!\n"
                     "Выбери анализатор с помощью кнопок ниже.",
                     reply_markup=create_keyboard())


# Обработка нажатий на кнопки
@bot.message_handler(func=lambda message: message.text in ['Использовать pymorphy2', 'Использовать mystem',
                                                           'Использовать оба анализатора'])
def handle_button_press(message):
    global current_analyzer
    if message.text == 'Использовать pymorphy2':
        current_analyzer = 'pymorphy2'
        bot.reply_to(message, "Анализатор переключён на pymorphy2.")
    elif message.text == 'Использовать mystem':
        current_analyzer = 'mystem'
        bot.reply_to(message, "Анализатор переключён на mystem.")
    elif message.text == 'Использовать оба анализатора':
        current_analyzer = 'both'
        bot.reply_to(message, "Анализатор переключён на оба (pymorphy2 и mystem).")


# Обработка текстовых сообщений для морфологического анализа
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text

    # Сохраняем результат анализа
    result = ""

    # Разбиваем ввод на слова
    words = re.findall(r'\w+', user_input)  # Используем регулярное выражение для нахождения слов

    for word in words:
        result += f"*Слово: {word}\n*"

        # Выполняем морфологический анализ в зависимости от выбранного анализатора
        if current_analyzer in ['pymorphy2', 'both']:
            result_pymorphy2 = analyze_with_pymorphy2(word)
            result += f"Морфологический разбор (pymorphy2):\n{result_pymorphy2}\n"

        if current_analyzer in ['mystem', 'both']:
            result_mystem = analyze_with_mystem(word)
            result += f"Морфологический разбор (mystem):\n{result_mystem}\n"

    # Отправляем объединённый результат пользователю
    bot.reply_to(message, result, parse_mode='Markdown')


# Запуск бота
bot.polling()
