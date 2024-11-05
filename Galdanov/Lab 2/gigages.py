from dotenv import load_dotenv
import os
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import telebot
import re
import requests

load_dotenv()
authorization_key = os.getenv('AUTHORIZATION_KEY')
tg_token = os.getenv('TG_TOKEN')
town_token = os.getenv('TOWN_TOKEN')

def lowercaser(town): # Чистит текст и делает его маленьким
    re.sub(r'[^а-яА-Я]', '', town)
    town = town.lower()
    return town

def towncheck(town): # Проверка на существование города
    town_check_url = f"https://api.openweathermap.org/data/2.5/weather?q={town}&appid=6fd2ce8b2ec49efc835527b62705ae3e"
    response = requests.get(town_check_url)
    if response.status_code == 200:
        return True
    else:
        return False

user_messages = {}
towns = {} #истоиря городов которая чекает повторяется город или нет

bot = telebot.TeleBot(tg_token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Здравствуйте, сыграем в города?')

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials=authorization_key, verify_ssl_certs=False)

system_main_question = ("Ты великий знаток городов, ты знаешь все названия городов в мире и помогаешь людям говоря названия городов которые им нужны. Однако ты также лаконичен и краток, ты даешь только название города без всяких описаний.")

# Города не должны повторяться, регистр должен быть один (Архангельск архангельск) +
# Сделать проверку на существование города +
# Сделать чтобы пользователь тоже проигрывал (сравнивать первую букву пользователя и последнюю букву предыдущего бота гигачата) +
# Сделать так чтобы можно было нескольким людям играть (история разная у каждого) +

@bot.message_handler(func=lambda message: True)
def analyze(message):
    user_id = message.chat.id
    current_town = lowercaser(message.text)
    lose_checker = False

    if user_id not in user_messages:
        user_messages[user_id] = [SystemMessage(content=system_main_question)]
    if user_id not in towns:
        towns[user_id] = []

    if list(towns[user_id]): #условие победы
        prev_answer_letter = towns[user_id][-1]
        if prev_answer_letter[-1] == "ъ" or prev_answer_letter[-1] == "ь":
            if prev_answer_letter[-2] != current_town[0]:
                lose_checker = True
        elif prev_answer_letter[-1] != current_town[0]:
            lose_checker = True

    if towncheck(current_town) is False:
        res = "Этого города не существует"
        bot.reply_to(message, res)
    else:
        if current_town in towns[user_id]:  # если город есть в списке истории то сказать что было
            res = "Этот город уже был"
            bot.reply_to(message, res)
        else:
            towns[user_id].append(
                current_town)  # в список городов добавляется ответ пользователя (он стоит тут ибо if выше чекает на уже сказанные города через current_town)

            if lose_checker is False:
                placeholder = message.text[-1]  # генерация промпта для гигачата
                if message.text[-1] == "ъ" or message.text[-1] == "ь":
                    placeholder = message.text[-2]
                user_input = f"Назови город начинающийся на {placeholder}"
                user_messages[user_id].append(HumanMessage(content=user_input))

                while True:  # генерация ответа от Гигачата, если город сгенерированный есть в списке, то генерируется новый
                    res = chat.invoke(user_messages[user_id])
                    if lowercaser(res.content) not in towns[user_id]:
                        break

                user_messages[user_id].append(res)
                towns[user_id].append(lowercaser(res.content))  # добавляется в историю городов ответ Гигачата
                bot.reply_to(message, res.content)
            else:
                res = "Вы проиграли, чтобы сыграть снова назовите город"
                bot.reply_to(message, res)
                towns.clear()

    print(towns)
    # Ответ сервиса



bot.polling(none_stop=True, interval=0)
