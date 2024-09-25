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
    y = "Вывод pymorphy3\n"
    for i in word:
        b = morph.parse(i)
        y = y + i + '\n' + '\n'.join(f"{n} {j}" for n, j in enumerate(b, start=1)) + '\n' #построение сообщения для бота, pymorphy3

    y = y + "Вывод mystem3\n"
    for i in word:
        b1 = m.analyze(i)[0]
        b1 = b1.get('analysis')
        b1 = b1[0]['gr']
        y = y + i + '\n' + b1 + '\n'

    bot.reply_to(message, y)

bot.polling(none_stop=True, interval=0)

#тестовое поле
# word = input()
# words = word.split(' ')
# y = ""
# for i in words:
#     b = morph.parse(i)
#     y = y + i + '\n' + '\n'.join(f"{n} {j}" for n, j in enumerate(b, start=1)) + '\n' #построение сообщения для бота, pymorphy3
# print(y)


# for i in words:
#    b1 = m.analyze(i)[0]
#    b1 = b1.get('analysis')
#    b1 = b1[0]['gr']
#    print(b1)

