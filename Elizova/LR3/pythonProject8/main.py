# pip install langchain langchain-community python-telegram-bot
import asyncio
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Авторизация в сервисе GigaChat
chat = GigaChat(credentials='мой api', verify_ssl_certs=False)

# Начальные сообщения
messages = [
    SystemMessage(
        content="Ты играешь в игру 'Города'. Игрок начинает с названия города, а ты должен будешь назвать город, который начинается на последнюю букву предыдущего города. Правила: 1. Название города должно быть реальным и находиться в любой стране. 2. Не повторяй уже названные города. 3. Игра ведется на русском языке."
    )
]

# Множество использованных городов, чтобы избежать повторений
used_cities = set()
player_active = True  # Флаг для отслеживания активности игрока


# Считываем города из файла в множество
def load_cities_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return set(city.strip().lower() for city in file.readlines())


# Загружаем города из файла
known_cities = load_cities_from_file('города.txt')


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global player_active
    player_active = True
    await update.message.reply_text(
        'Привет! Давай сыграем в игру "Города". Я начну с названия города, а ты должен будешь назвать город, который начинается на последнюю букву моего города. Первый ход твой!')


# Функция для ожидания ответа от игрока
async def wait_for_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global player_active
    await asyncio.sleep(15)  # Ожидание 15 секунд
    if player_active:
        await update.message.reply_text('Время вышло! Вы проиграли. Игра окончена.')
        used_cities.clear()  # Очистить использованные города
        player_active = False  # Игрок больше не активен


# Обработчик входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages, player_active  # Указываем, что используем глобальные переменные
    user_input = update.message.text.strip().lower()  # Получаем текст сообщения от пользователя

    if not player_active:
        return  # Если игрок не активен, игнорируем сообщения

    # Проверяем, был ли город уже назван
    if user_input in used_cities:
        await update.message.reply_text('Этот город уже был назван. Попробуйте другой.')
        return

    # Проверяем, существует ли город в известном наборе
    if user_input not in known_cities:
        await update.message.reply_text('Этот город не существует. Попробуйте другой.')
        return

    # Добавляем город в набор использованных
    used_cities.add(user_input)
    messages.append(HumanMessage(content=user_input))  # Добавляем сообщение игрока

    # Получаем последнюю букву введенного города для ответа бота
    last_char = user_input[-1].lower()

    # Проверяем, является ли последняя буква мягким знаком
    if last_char == 'ь':
        # Если да, используем предпоследнюю букву
        if len(user_input) > 1:
            last_char = user_input[-2].lower()
        else:
            await update.message.reply_text(
                'Невозможно использовать предпоследнюю букву, так как город состоит из одного символа.')
            return

    bot_response = f"Твой город: {user_input}. Теперь мой ход. Я назову город на букву '{last_char}'."

    # Сбросим сообщения и добавим новое системное сообщение перед обращением к API
    messages = [SystemMessage(content=bot_response)]
    messages.append(HumanMessage(content=user_input))

    res = chat(messages)  # Получаем ответ от GigaChat

    # Проверяем, был ли ответ бота уженазван
    if res.content.lower() in used_cities:
        await update.message.reply_text(
            f'Я не могу назвать город "{res.content}", так как он уже был использован. Попробую еще раз.')
        return

    # Добавляем ответ бота в использованные города
    used_cities.add(res.content.lower())
    await update.message.reply_text(res.content)  # Отправляем ответ пользователю

    # Запускаем таймер ожидания ответа от игрока
    asyncio.create_task(wait_for_response(update, context))


def main() -> None:
    # Создаем приложение Telegram с токеном бота
    application = ApplicationBuilder().token("мой токен").build()

    # Добавляем обработчики команд и текстовых сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()  # Запускаем бота


if __name__ == '__main__':
    main()  # Запускаем основную функцию