from langchain.schema import HumanMessage
from langchain_community.chat_models.gigachat import GigaChat
import os
from dotenv import load_dotenv

load_dotenv()
GIGATOKEN = os.getenv('GIGATOKEN')

class GigaConnector:
    def __init__(self, verify_ssl_certs=False): #Added verify_ssl_certs
        self.chat_model = GigaChat(credentials=GIGATOKEN, verify_ssl_certs=verify_ssl_certs)

    def generate_city(self, letter, used_cities):
        """
        Генерирует город на указанную букву, исключая уже использованные города.
        """
        # Фильтруем только города, начинающиеся с нужной буквы
        filtered_cities = [city for city in used_cities if city.lower().startswith(letter.lower())]
        forbidden_cities = ', '.join(filtered_cities)
        query = (
            f"Напиши один город на букву '{letter.upper()}'. "
            f"Не называй следующие города: {forbidden_cities}. "
            f"Ответь одним словом."
        )

        # Отправляем запрос в GigaChat
        response = self.chat_model.invoke([HumanMessage(content=query)])

        if response and response.content:
            city = response.content.strip().rstrip(".")  # Убираем лишние знаки
            print(city)
            return city
        return None
    def is_exsit(self, city):
        response = self.chat_model.invoke([HumanMessage(content=f"Существует ли город с названием {city}? Ответ: да или нет")])
        return 'да' in response.content.lower()
        # return response.content if response and response.content else None

if __name__ == "__main__":
    llm = GigaConnector()
    x = llm.generate_city('А')
    y = llm.is_exsit('Архангельск')
    print(x)
    print(y)
