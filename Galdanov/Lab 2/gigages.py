from dotenv import load_dotenv
import os
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import telebot

load_dotenv()
authorization_key = os.getenv('AUTHORIZATION_KEY')
tg_token = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(tg_token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Здравствуйте, я профессиональный игровой журналист по нишевым играм, задайте ваш вопрос.')


# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=authorization_key, verify_ssl_certs=False)

system_main_question = "Ты профессиональный игровой журналист по нишевым играм, который знает многое про малоизвестные японские, корейские и западые игры. Игры которые снискали небольшую популярность, но верную фанбазу."

messages = [
    SystemMessage(
        content=system_main_question
    )
]


@bot.message_handler(func=lambda message: True)
def analyze(message):
    user_input = str(message)
    messages.append(HumanMessage(content=user_input))
    res = chat.invoke(messages)
    messages.append(res)
    # Ответ сервиса
    bot.reply_to(message, res.content)


bot.polling(none_stop=True, interval=0)