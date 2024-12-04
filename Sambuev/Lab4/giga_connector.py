from langchain.schema import HumanMessage
from langchain_community.chat_models.gigachat import GigaChat
import config


class GigaConnector:
    def __init__(self):
        gigachat_api_key = config.GIGACHAT_API_KEY
        self.chat = GigaChat(credentials=gigachat_api_key, verify_ssl_certs=False)

    def get_town(self, first_letter):
        """Получает название города на заданную букву через GigaChat."""
        prompt = f"Назови город на букву '{first_letter}', ответь одним словом."
        response = self.chat([HumanMessage(content=prompt)])
        return response.content.strip('.')
