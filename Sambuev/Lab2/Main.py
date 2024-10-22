import telebot
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
import config

# Используем токен и ключ из config.py
bot_token = config.TELEGRAM_BOT_TOKEN
gigachat_api_key = config.GIGACHAT_API_KEY

# Авторизация в GigaChat
chat = GigaChat(credentials=gigachat_api_key, verify_ssl_certs=False)

# Инициализация телеграмм бота
bot = telebot.TeleBot(bot_token)

# Инициализация сообщений
messages = [
    SystemMessage(
        content="Ты хардкорный игрок в видеоигры, специализирующийся на спидранах в различных проектах."
    )
]


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Получаем текст от пользователя
    user_input = message.text
    messages.append(HumanMessage(content=user_input))

    # Отправляем сообщение в GigaChat и получаем ответ
    res = chat(messages)
    messages.append(res)

    # Отправляем ответ пользователю в Telegram
    bot.send_message(message.chat.id, res.content)


# Запуск бота
bot.polling()