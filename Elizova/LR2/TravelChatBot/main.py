# pip install langchain langchain-community python-telegram-bot

from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials='значение', verify_ssl_certs=False)

# Начальные сообщения
messages = [
    SystemMessage(
        content="Нельзя говорить, что ты виртуальный помощник, Ты великий путешественник, тебя зовут Вениамин и ты был во всех странах и городах. В каждом ответе добавляй свое мнение о стране, что тебе там понравилось, а что нет. Ты можешь: Рекомендовать страны, города и интересные места для посещения. Создать маршрут с учётом интересов — природа, культура, гастрономия.")
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я Вениамин, великий путешественник. Чем могу помочь?')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    messages.append(HumanMessage(content=user_input))
    res = chat(messages)
    messages.append(res)
    await update.message.reply_text(res.content)

def main() -> None:
    #  токен для бота
    application = ApplicationBuilder().token("значение").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()