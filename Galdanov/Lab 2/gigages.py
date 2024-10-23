from dotenv import load_dotenv
import os
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import telebot

load_dotenv()
authorization_key = os.getenv('AUTHORIZATION_KEY')
tg_token = os.getenv('TG_TOKEN')

user_messages = {}
towns = {}

bot = telebot.TeleBot(tg_token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Здравствуйте, сыграем в города?')


# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=authorization_key, verify_ssl_certs=False)

system_main_question = ("Ты великий знаток городов, ты знаешь все названия городов в мире и помогаешь людям говоря названия городов которые им нужны. Однако ты также лаконичен и краток, ты даешь только название города без всяких описаний.")

# Города не должны повторяться, регистр должен быть один (Архангельск архангельск)
# Сделать проверку на существование города
# Проверку на победителя, победил пользователь и тд и тп.
# Сделать чтобы пользователь тоже проигрывал (сравнивать первую букву пользователя и последнюю букву предыдущего бота гигачата)
# Сделать так чтобы можно было нескольким людям играть (история разная у каждого)

@bot.message_handler(func=lambda message: True)
def analyze(message):
    user_id = message.chat.id

    towns[user_id].append(message.text)

    if user_id not in user_messages:
        user_messages[user_id] = [SystemMessage(content=system_main_question)]

    placeholder = message.text[-1]

    if message.text[-1] == "ъ" or message.text[-1] == "ь":
        placeholder = message.text[-2]

    user_input = f"Назови город начинающийся на {placeholder}"

    user_messages[user_id].append(HumanMessage(content=user_input))
    res = chat.invoke(user_messages[user_id])
    user_messages[user_id].append(res)
    # Ответ сервиса
    bot.reply_to(message, res.content)


bot.polling(none_stop=True, interval=0)
