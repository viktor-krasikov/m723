import pymorphy3
import telebot
from pymystem3 import Mystem

morph = pymorphy3.MorphAnalyzer()
m = Mystem()
bot = telebot.TeleBot('8145074076:AAH8EW_lymG2uk-dw5euT9y6ZpzdDVXka3k')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Введите слово для анализа')

@bot.message_handler(func=lambda message: True)
def analyze(message):
    word = message.text
    word = word.split()
    answer = "Вывод pymorphy3\n"
    tag_builder = []
    for i in word:
        b = morph.parse(i)
        for k in b:
            tag_builder.append(str(k.tag))
        answer = answer + i + '\n' + '\n' + '\n'.join(f"{n} {j}" for n, j in enumerate(tag_builder, start=1)) + '\n' #построение сообщения для бота, pymorphy3

    answer_2 = "Вывод mystem3\n"
    for i in word:
        b1 = m.analyze(i)[0]
        b1 = b1.get('analysis')
        if b1:
            b1 = b1[0]['gr']  # Пытаемся получить грамматическую информацию
        else:
            b1 = "Анализ не содержит данных."
        answer_2 = answer_2 + i + '\n' + b1 + '\n'

    bot.reply_to(message, answer)
    bot.reply_to(message, answer_2) #считаю что вывод в двух сообщениях выглядит лучше, особенно когда слов много

bot.polling(none_stop=True, interval=0)

#тестовое поле
# word = input()
# words = word.split(' ')
# answer = ""
# tag_builder = []
# for i in words:
#     b = morph.parse(i)
#     for k in b:
#         tag_builder.append(str(k.tag))
#     answer = answer + i + '\n' + '\n'.join(f"{n} {j}" for n, j in enumerate(tag_builder, start=1)) + '\n' #построение сообщения для бота, pymorphy3
# print(answer)
# программа для обращения к гигачату, текстовый запрос и текстовый ответ

# word = input()
# words = word.split(' ')
# for i in words:
#    b1 = m.analyze(i)[0]
#
#    b1 = b1.get('analysis')
#    if b1:
#        b1 = b1[0]['gr']  # Пытаемся получить грамматическую информацию
#        print(b1)
#    else:
#        print("Анализ не содержит данных.")


