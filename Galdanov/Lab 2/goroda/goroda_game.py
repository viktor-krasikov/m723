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

    def towncheck(self, town): #проверка на существование города
        town_check_url = f"https://api.openweathermap.org/data/2.5/weather?q={town}&appid={self.town_token}"
        response = requests.get(town_check_url)
        return response.status_code == 200

    def lowercaser(self, town):  #сделать так чтобы чистил пробелы, запятые и точки
        re.sub(r'[^\w.а-яА-Я]', '', town)
        town = town.lower()
        return town

    def letter_check(self, word): # проверка на Ъ Ь Ы у последней буквы
        if word[-1] == "ъ" or word[-1] == "ь" or word[-1] == "ы":
            return word[-2]
        else:
            return word[-1]

    def giveup_checker(self, message):
        message = message.lower()
        pattern = r'\b(я\s*сдаюсь|сдаюсь|сдамся|сдаюсь|сдатьс|сдаюс\s*я)\b'
        if re.search(pattern, message):
            return True
        else:
            return False

    def reset_game(self):
        self.towns.clear()

    def town_game(self, current_town):
        current_town = self.lowercaser(current_town)
        last_letter = current_town[0] #чек для 1го раза
        if self.towns:
            last_letter = self.letter_check(self.towns[-1])
        res = ""


        if self.giveup_checker(current_town):
            print("Хорошо, давайте начнем снова")
        else:
            if last_letter == current_town[0]:

                if current_town in self.towns:
                    res = "Этот город уже был"
                else:
                    self.towns.append(current_town)  # добавление в список городов уже сыгранных
                    if self.towncheck(current_town) is False:
                        res = "Этого города не существует"
                    else:
                        placeholder = self.letter_check(current_town)
                        for i in range(5):
                            res = gigacon.generate_town(placeholder, self.towns)
                            res = self.lowercaser(res)
                            if res not in self.towns:
                                self.towns.append(res)
                                break
                            if i == 4:
                                res = "Вы выйграли, я не смог придумать город"
                                self.reset_game()
            else:
                res = f"Ваш город не начинается на {last_letter} попробуйте ещё раз"

        return res
