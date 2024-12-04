from giga_connector import GigaConnector
import random


class GorodaGame:
    def __init__(self):
        self.user_data = {}
        self.llm = GigaConnector()

    def reset_game(self, user_id):
        """Инициализация или сброс данных для пользователя."""
        self.user_data[user_id] = {
            "history": [],
            "target_score": random.randint(5, 20),
            "current_score": 0,
            "last_bot_city": None,
        }

    def get_last_significant_letter(self, city):
        """Возвращает последнюю значимую букву города (не 'ь', 'ъ', 'ы')."""
        for letter in reversed(city):
            if letter.lower() not in "ьъы":
                return letter.lower()
        return city[-1].lower()

    def start(self, user_id):
        """Начало игры для пользователя."""
        if user_id not in self.user_data:
            self.reset_game(user_id)
        return f"Игра началась! Наберите {self.user_data[user_id]['target_score']} очков, чтобы выиграть."

    def stop(self, user_id):
        """Завершение игры для пользователя."""
        if user_id in self.user_data:
            del self.user_data[user_id]
        return "Игра окончена. Спасибо за игру!"

    def next(self, user_id, town):
        """Обрабатывает ход игрока."""
        if user_id not in self.user_data:
            self.reset_game(user_id)

        game_data = self.user_data[user_id]

        # Проверка: город уже был назван
        if town in game_data["history"]:
            return "Этот город уже был назван. Попробуйте другой."

        # Проверка: город начинается на правильную букву
        if game_data["last_bot_city"]:
            required_letter = self.get_last_significant_letter(game_data["last_bot_city"])
            if town[0].lower() != required_letter:
                return f"Ваш город должен начинаться на букву '{required_letter.upper()}'."

        # Обновление истории и счета
        game_data["history"].append(town)
        game_data["current_score"] += 1

        # Проверка: достигнута ли цель
        if game_data["current_score"] >= game_data["target_score"]:
            self.reset_game(user_id)
            return f"Поздравляем! Вы выиграли, набрав {game_data['target_score']} очков."

        # Ответ бота
        last_letter = self.get_last_significant_letter(town)
        bot_city = self.llm.get_town(last_letter)

        # Проверка: уникальность ответа бота
        while bot_city in game_data["history"]:
            bot_city = self.llm.get_town(last_letter)

        game_data["last_bot_city"] = bot_city
        game_data["history"].append(bot_city)

        return f"{bot_city}. Ваш ход, назовите город на букву '{self.get_last_significant_letter(bot_city).upper()}'."
