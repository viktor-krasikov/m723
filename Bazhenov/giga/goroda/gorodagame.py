from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import threading
from gigia_connector import GigaConnector  # Подключение отдельного модуля для GigaChat


class GorodaGame:
    def __init__(self):
        self.cities_set = self.load_cities("txt-cities-russia.txt")
        self.user_timers = {}
        self.time_is_up_funcs = {}
        self.user_played_cities = {}
        self.city_info = {}
        self.connector = GigaConnector()  # Инициализация коннектора для GigaChat
        self.default_messages = [SystemMessage(content="Ты играешь в города. Каждый участник называет реально существующий город России. Название города должно начинаться на букву, которой оканчивается название предыдущего города, за исключением 'ь' и 'ъ'.")]

    def load_cities(self, filename):
        """Загружает список городов из файла и возвращает его в виде множества."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return set(city.strip().lower() for city in file.readlines())
        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
            return set()
    def is_city_exist(self, city_name):
        """Проверяет, существует ли город в загруженном списке."""
        return city_name.lower() in self.cities_set

    def extract_last_letter(self, city):
        """Извлекает последнюю значимую букву названия города."""
        last_letter = city.strip()[-1]
        return last_letter if last_letter not in "ьъ" else city.strip()[-2]

    def normalize_city_name(self, city):
        """Нормализует название города, убирая окончания."""
        city = city.lower().strip()
        endings = ["ий", "ый", "ой", "ая", "яя", "ое", "ье", "ое", "а", "я", "ъ", "ь"]
        for ending in endings:
            if city.endswith(ending):
                return city[:-len(ending)]
        return city

    def is_city_used(self, city, played_cities):
        """Проверяет, был ли город уже назван."""
        print(city)
        normalized_city = self.normalize_city_name(city)
        return normalized_city in (self.normalize_city_name(c) for c in played_cities)

    def stop_game(self, chat_id):
        if chat_id in self.user_timers:
            self.user_timers[chat_id].cancel()
        del self.user_played_cities[chat_id]
        del self.city_info[chat_id]
        del self.user_timers[chat_id]
        del self.time_is_up_funcs[chat_id]

    def start_timer(self, chat_id, timeout=60):
        if chat_id in self.user_timers:
            self.user_timers[chat_id].cancel()
        timer = threading.Timer(timeout, self.time_is_up_funcs[chat_id], [chat_id])
        self.user_timers[chat_id] = timer
        timer.start()

    def start_game(self, chat_id, time_is_up_fn=None):
        """Начинает новую игру."""
        self.user_played_cities[chat_id] = []
        self.city_info[chat_id] = None
        # if chat_id in self.user_timers:
        #     self.user_timers[chat_id].cancel()
        self.time_is_up_funcs[chat_id] = time_is_up_fn
        return "Игра началась! Назовите первый город."

    # is_started
    def __contains__(self, chat_id):
        return chat_id in self.time_is_up_funcs

    def next(self, chat_id, user_input):

        if chat_id not in self:
            return "Сначала начните игру!"

        # Проверка, был ли город уже использован
        if self.is_city_used(user_input, self.user_played_cities[chat_id]):
            return f"Город '{user_input}' уже использован. Попробуйте другой."

        # Проверка соответствия первой буквы
        if self.user_played_cities[chat_id]:
            last_letter = self.extract_last_letter(self.user_played_cities[chat_id][-1])
            if user_input[0].lower() != last_letter:
                return f"Город '{user_input}' должен начинаться на букву '{last_letter.upper()}'"

        # Проверка существования города
        try:
            if not self.connector.is_exsit(user_input):# not self.is_city_exist(user_input):
                return f"Город '{user_input}' не существует."
        except Exception as e:
            return f"Ошибка при проверке города: {e}"

        # Добавляем город в историю
        self.user_played_cities[chat_id].append(user_input)


        # Генерация следующего города
        last_letter_of_user_word = self.extract_last_letter(user_input.lower())
        for _ in range(5):
            next_city = self.connector.generate_city(
                last_letter_of_user_word,
                self.user_played_cities[chat_id]
            )

            # if next_city and not self.is_city_used(next_city, self.user_played_cities[chat_id]):
            if next_city:
                if (not self.is_city_used(next_city, self.user_played_cities[chat_id])
                        and next_city[0].lower() == last_letter_of_user_word):
                    self.user_played_cities[chat_id].append(next_city)
                    self.start_timer(chat_id)
                    self.city_info[chat_id] = next_city
                    return next_city
        self.stop_game(chat_id)
        return f"Я проиграл! не могу придумать город на букву - {last_letter_of_user_word}"
    # def detail(self, chat_id):
    #     if chat_id in self.city_info and self.city_info[chat_id]:
    #         detail = self.connector.more_info_city(self.city_info[chat_id])
    #     else:
    #         detail = "Нет данных для показа. Попробуйте снова после следующего хода."
    #     return detail
    def detail(self, mes):
        detail = self.connector.more_info_city(mes)
        return detail

