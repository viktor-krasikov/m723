import telebot
import json
from pymystem3 import Mystem
import spacy
from pymorphy2 import MorphAnalyzer

nlp = spacy.load("ru_core_news_sm")
morph = MorphAnalyzer()

TOKEN = "7638458680:AAGklvEutJxXaIm0vPDTXTW6epWlbT159HU"

bot = telebot.TeleBot(TOKEN)

current_analyzer = "mystem"  # Изначально выбран Mystem

def analyze_text_mystem(text):
    m = Mystem()
    analysis = m.analyze(text)
    output = ""
    for i, word in enumerate(analysis):
        if word.get("analysis"):
            for j, ana in enumerate(word["analysis"]):
                lex = ana["lex"]
                gr = ana["gr"]
                if j == 0:
                    output += f"Слово: {word['text']}\n"
                output += f"  - Вариант {j+1}:\n"
                output += f"    - Лемма: {lex}\n"
                output += f"    - Часть речи: {gr[0]}\n"  # Первая буква кода части речи
                output += f"    - Морфологические признаки: {gr}\n\n"
    return output

def analyze_text_spacy(text):
    # Пропускаем текст через NLP модель
    doc = nlp(text)

    output = ""
    for i, token in enumerate(doc):
        if i == 0:
            output += f"Слово: {token.text}\n"
        output += f"  - Вариант {i+1}:\n"
        output += f"    - Часть речи: {token.pos_} ({spacy.explain(token.pos_)})\n"  # Часть речи
        output += f"    - Лемма: {token.lemma_}\n"  # Лемма (начальная форма слова)
        output += f"    - Морфологические признаки: {token.morph}\n\n"  # Доп. морфологическая информация
    return output

def analyze_text_pymorphy(text):
    output = ""
    words = text.split()
    for i, word in enumerate(words):
        parses = morph.parse(word)
        if i == 0:
            output += f"Слово: {word}\n"
        for j, parse in enumerate(parses):
            output += f"  - Вариант {j+1}:\n"
            output += f"    - Лемма: {parse.normal_form}\n"
            output += f"    - Часть речи: {parse.tag.POS}\n"
            output += f"    - Морфологические признаки: {parse.tag}\n\n"
    return output

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Mystem", "SpaCy", "Pymorphy", "All")
    bot.reply_to(message, "Привет! Выбери анализатор:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Mystem", "SpaCy", "Pymorphy", "All"])
def handle_analyzer_choice(message):
    global current_analyzer  # Изменяем глобальную переменную
    current_analyzer = message.text.lower()
    bot.reply_to(message, f"Выбрано: {current_analyzer}")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global current_analyzer
    text = message.text

    if current_analyzer == "mystem":
        response = analyze_text_mystem(text)
        bot.reply_to(message, f"```\n{response}\n```")
    elif current_analyzer == "spacy":
        response = analyze_text_spacy(text)
        bot.reply_to(message, f"```\n{response}\n```")
    elif current_analyzer == 'pymorphy':
        response = analyze_text_pymorphy(text)
        bot.reply_to(message, f"```\n{response}\n```")
    elif current_analyzer == 'all':
        response_mystem = analyze_text_mystem(text)
        response_spacy = analyze_text_spacy(text)
        response_pymorphy = analyze_text_pymorphy(text)
        print(f"```\n mystem: {response_mystem}\n\n spacy: \n{response_spacy}\n\n pymorphy: \n{response_pymorphy}\n```")
        bot.reply_to(message,f"```\n mystem: \n{response_mystem}\n\n spacy: \n{response_spacy}\n\n pymorphy: \n{response_pymorphy}\n```")

bot.polling()
