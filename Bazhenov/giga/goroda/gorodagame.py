from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import threading
from gigia_connector import GigaConnector

class GorodaGame:
    def __init__(self): # Changed parameter name
        self.user_histories = {}
        self.user_timers = {}
        self.user_played_cities = {}
        self.city_info = {}
        self.connector = GigaConnector() # Pass gigachat instance
        self.default_messages = [SystemMessage(content="Ты играешь в города. Каждый участник называет реально существующий город. Название города должно начинаться на букву, которой оканчивается название предыдущего города, за исключением 'ь' и 'ъ'.")]

    def extract_last_letter(self, city):
        last_letter = city.strip()[-1]
        return last_letter if last_letter not in "ьъ" else city.strip()[-2]

    def normalize_city_name(self, city):
        city = city.lower().strip()
        endings = ["ий", "ый", "ой", "ая", "яя", "ое", "ье", "ое", "а", "я", "ъ", "ь"]
        for ending in endings:
            if city.endswith(ending):
                return city[:-len(ending)]
        return city

    def is_city_used(self, city, played_cities):
        normalized_city = self.normalize_city_name(city)
        first_letter = normalized_city[0].lower()
        used = any(normalized_city == self.normalize_city_name(c) for c in played_cities if self.normalize_city_name(c)[0].lower() == first_letter)
        return used

    def reset_game(self, chat_id):
        self.user_histories[chat_id] = self.default_messages.copy()
        self.user_played_cities[chat_id] = []
        self.city_info[chat_id] = None
        if chat_id in self.user_timers:
            self.user_timers[chat_id].cancel()

    def start_game(self, chat_id):
        self.reset_game(chat_id)
        return "Игра началась! Назовите город."

    def next(self, message):
        chat_id = messagge.chat.id
        user_input = message.text.strip().capitalize()

        if chat_id not in self.user_played_cities:
            self.user_played_cities[chat_id] = []
        if chat_id not in self.user_histories:
            self.user_histories[chat_id] = self.default_messages.copy()

        if self.is_city_used(user_input, self.user_played_cities[chat_id]):
            return f"Город '{user_input}' уже использован."
        if self.user_played_cities[chat_id]: # переделать last_letter
            last_letter = self.extract_last_letter(self.user_played_cities[chat_id][-1])
            if user_input[0].lower() != last_letter:
                return f"Город '{user_input}' не начинается на букву '{last_letter}'."

        try:
            verification_response = self.connector.is_exsit(user_input)
            if not(verification_response):
                return f"Город '{user_input}' не существует."
            self.user_played_cities[chat_id].append(user_input)
        except Exception as e: #Added exception handling
            return f"Произошла ошибка: {e}"
        city = self.connector.generate_city(user_input[-1])
        self.user_histories[chat_id].append(city)
        return city