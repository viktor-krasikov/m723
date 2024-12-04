import telebot
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Инициализация бота и API ключей
bot_token = config.TELEGRAM_BOT_TOKEN
gigachat_api_key = config.GIGACHAT_API_KEY
chat = GigaChat(credentials=gigachat_api_key, verify_ssl_certs=False)
bot = telebot.TeleBot(bot_token)

# Словарь для хранения сообщений пользователей и история городов
user_messages = {}
history_game = []

# Системное сообщение с правилами игры
system_message = SystemMessage(
    content="Ты играешь со мной в игру 'Города'. Называй город, который ещё не был назван, и начинающийся на последнюю значимую букву города собеседника. Пример: Москва — Астрахань — Новосибирск и т.д."
)

def get_last_significant_letter(city):
    """Возвращает последнюю значимую букву города (не 'ь', 'ъ', 'ы')."""
    for letter in reversed(city):
        if letter.lower() not in "ьъы":
            return letter.lower()
    return city[-1].lower()

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_name = message.from_user.username or message.from_user.first_name

    # Инициализация сообщений для нового пользователя
    if user_id not in user_messages:
        user_messages[user_id] = [system_message]

    # Получаем текст от пользователя
    user_input = message.text.strip()

    # Проверка, был ли город уже назван
    if user_input in history_game:
        bot.send_message(user_id, "Этот город уже был назван. Попробуй другой.")
        return

    # Получаем последнюю значимую букву города
    last_letter = get_last_significant_letter(user_input)

    # Генерация сообщения для GigaChat
    prompt = f"Назови город на букву '{last_letter}'"
    user_messages[user_id].append(HumanMessage(content=prompt))

    # Логирование
    logging.info(f"User [{user_name} (ID: {user_id})]: {user_input}")

    # Отправляем сообщение в GigaChat и получаем ответ
    res = chat(user_messages[user_id])
    user_messages[user_id].append(res)

    # Обновляем историю и отправляем ответ пользователю
    history_game.append(user_input)
    history_game.append(res.content)
    bot.send_message(user_id, res.content)

    # Логирование ответа бота
    logging.info(f"Bot [{user_name} (ID: {user_id})]: {res.content}")

    # Вывод истории в консоль
    print("История игры:", history_game)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)