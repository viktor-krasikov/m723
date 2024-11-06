import re
from dotenv import load_dotenv
import requests
import os
from .gigachat_con import GigaCon

gigacon = GigaCon()


class GorodaGame:
    def __init__(self):
        self.towns = []  # история городов
        load_dotenv()
        self.town_token = os.getenv('TOWN_TOKEN')

    def towncheck(self, town):
        town_check_url = f"https://api.openweathermap.org/data/2.5/weather?q={town}&appid={self.town_token}"
        response = requests.get(town_check_url)
        return response.status_code == 200

    def lowercaser(self, town):  # TODO: сделать так чтобы чистил пробелы, запятые и точки
        re.sub(r'[^а-яА-Я]', '', town)
        town = town.lower()
        return town

    def town_game(self, current_town):
        current_town = self.lowercaser(current_town)
        last_letter = current_town[0]
        if self.towns:
            last_letter = self.towns[-1][-1]
        res = ""

        # TODO: сделать так чтобы был ответ на сообщение "Я сдаюсь"
        if current_town[0] == last_letter:
            if current_town in self.towns:
                res = "Этот город уже был"
            else:
                if self.towncheck(current_town) is False:
                    res = "Этого города не существует"
                else:
                    placeholder = current_town[-1]  # проверка на Ъ Ь Ы у последней буквы
                    if current_town[-1] == "ъ" or current_town[-1] == "ь" or current_town[-1] == "ы":
                        placeholder = current_town[-2]
                    res = gigacon.generate_town(placeholder, self.towns)
        else:
            res = f"Ваш город не начинается на {last_letter} попробуйте ещё раз"
        return res
