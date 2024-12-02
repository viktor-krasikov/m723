import telebot
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

@bot.message_handler(func=lambda message: True)
def on_message_from_user(message):
    messages.append(HumanMessage(content=message.text))
    res = chat(messages)
    messages.append(res)
    bot.reply_to(message, res.content)



# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=read_file('tokengigachat'), verify_ssl_certs=False)

messages = [
    SystemMessage(
        content="Ты - виртуальный ветеринар, готовый помочь с вопросами о заботе и здоровье домашних питомцев. Ты можешь дать советы по уходу за животными, информацию о заболеваниях и подсказать, какие шаги предпринять в случае возникновения проблем со здоровьем домашнего питомца"
    )
]

token = read_file('tokentg')
bot = telebot.TeleBot(token)

# Запускаем бота
bot.infinity_polling()