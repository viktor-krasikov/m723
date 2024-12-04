from dotenv import load_dotenv
import os
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat


class GigaCon:
    def __init__(self):
        load_dotenv()
        self.authorization_key = os.getenv('AUTHORIZATION_KEY')
        # Авторизация в сервисе GigaChat
        self.chat = GigaChat(credentials=self.authorization_key, verify_ssl_certs=False)

    def generate_town(self, letter, history):
        if history:
            user_input = f"Назови город начинающийся на {letter} и не являющися городом из этого списка {history}. Ответь одним словом"
        else:
            user_input = f"Назови город начинающийся на {letter}. Ответь одним словом"
        gigachat_gen_answer = self.chat([HumanMessage(content=user_input)])
        return gigachat_gen_answer.content
