import requests


class BaseApiRequestError(Exception):
    """
    Базовый класс для остальных эксепшнов
    """
    def __init__(self, message: str = 'BaseApiRequestError was raised'):
        self.message = message


class RequestError(BaseApiRequestError):
    def __init__(self, message: str = 'Request error'):
        super().__init__(message=message)


class UnexpectedResponse(BaseApiRequestError):
    def __init__(self, response: requests.Response, message: str = 'Неожиданный ответ с сервера'):
        super().__init__(message=message)
        self.response = response
        self.code = response.status_code
        try:
            self.body = response.json()
        except ValueError:
            self.body = response.text


class JsonDecodeError(BaseApiRequestError):
    def __init__(self, body_text: str, message: str = 'Couldn\'t decode response\'s body as json'):
        super().__init__(message=message)
        self.body_text = body_text
