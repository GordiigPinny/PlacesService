import requests
from typing import Dict, Any, Union, Callable, List, Tuple
from ApiRequesters.exceptions import RequestError, UnexpectedResponse, JsonDecodeError


class BaseApiRequester:
    """
    Базовый класс для общения микросервисов
    """
    class METHODS:
        """
        Енум для HTTP-методов
        """
        GET = 'GET'
        POST = 'POST'
        PATCH = 'PATCH'
        DELETE = 'DELETE'

    def __init__(self):
        self.host = 'http://127.0.0.1:8000/'
        self.api_url = self.host + 'api/'
        self.token_prefix = 'Bearer'

    def _validate_return_code(self, response: requests.Response, expected_code: int, throw: bool = True) -> bool:
        """
        Валидация кода возврата с ожидаемым
        @param response: Объект-ответ сервера
        @param expected_code: Ожидаемый код возврата
        @param throw: Кидать ли эксепшн, если код не равен ожидаемому
        @return: True, если код возврата равен ожидаемому
        """
        if response.status_code != expected_code:
            if throw:
                raise UnexpectedResponse(response)
            else:
                return False
        return True

    def _get_json_from_response(self, response: requests.Response, throw: bool = True) -> Union[Dict, List, str]:
        """
        Получение джсона из ответа
        @param response: Объект-ответ сервера
        @param throw: Кидать ли эксепшн, если в ответе не джсон
        @return: Джсон, либо текст ответа, если throw = False
        """
        try:
            return response.json()
        except ValueError:
            if throw:
                raise JsonDecodeError(body_text=response.text)
            else:
                return response.text

    def _create_auth_header_tuple(self, token: str) -> Tuple[str, str]:
        """
        Возврат кортежа-хэдера авторизации
        @param token: Токен
        @return: Кортеж вида ('Authorization': <token>)
        """
        return 'Authorization', f'{self.token_prefix} {token}'

    def _make_request(self, method: Callable, uri, headers, params, data) -> requests.Response:
        """
        Непосредственно делает запрос на сторонний сервис
        @param method: Функция из либы requests
        @param uri: Куда стучимся
        @param headers: Хэдеры
        @param params: Кьюери-параметры
        @param data: - Боди (джсон)
        @return: Ответ внешнего сервиса
        """
        try:
            return method(uri, params, json=data, headers=headers)
        except requests.exceptions.RequestException:
            raise RequestError()

    def make_request(self, method: str, path_suffix: str, headers: Union[Dict[str, Any], None] = None,
                     data: Union[Dict[str, Any], List[Any], None] = None,
                     params: Union[Dict[str, Any], None] = None) -> requests.Response:
        """
        Публичный метод реквеста, самый-самый базовый
        @param method: Строка из внутреннего класса-енума METHODS
        @param path_suffix: Суффикс, добавляемый после self.api_url
        @param headers: Хэдеры
        @param params: Кьюери-параметры
        @param data: - Боди (джсон)
        @return: Ответ внешнего сервиса
        """
        if method == self.METHODS.GET:
            return self._make_request(method=requests.get, uri=self.api_url + path_suffix, headers=headers,
                                      params=params, data=data)
        elif method == self.METHODS.POST:
            return self._make_request(method=requests.post, uri=self.api_url + path_suffix, headers=headers,
                                      params=params, data=data)
        elif method == self.METHODS.PATCH:
            return self._make_request(method=requests.patch, uri=self.api_url + path_suffix, headers=headers,
                                      params=params, data=data)
        elif method == self.METHODS.DELETE:
            return self._make_request(method=requests.delete, uri=self.api_url + path_suffix, headers=headers,
                                      params=params, data=data)
        else:
            raise RequestError('Wrong HTTP method')

    def get(self, path_suffix: str, headers: Union[Dict[str, Any], None] = None,
            data: Union[Dict[str, Any], List[Any], None] = None, params: Union[Dict[str, Any], None] = None) -> requests.Response:
        """
        Гет-запрос
        @param path_suffix: Суффикс, добавляемый после self.api_url
        @param headers: Хэдеры
        @param params: Кьюери-параметры
        @param data: - Боди (джсон)
        @return: Ответ внешнего сервиса
        """
        return self.make_request(self.METHODS.GET, path_suffix=path_suffix, headers=headers, data=data, params=params)

    def post(self, path_suffix: str, headers: Union[Dict[str, Any], None] = None,
            data: Union[Dict[str, Any], List[Any], None] = None, params: Union[Dict[str, Any], None] = None) -> requests.Response:
        """
        Пост-запрос
        @param path_suffix: Суффикс, добавляемый после self.api_url
        @param headers: Хэдеры
        @param params: Кьюери-параметры
        @param data: - Боди (джсон)
        @return: Ответ внешнего сервиса
        """
        return self.make_request(self.METHODS.POST, path_suffix=path_suffix, headers=headers, data=data, params=params)

    def patch(self, path_suffix: str, headers: Union[Dict[str, Any], None] = None,
            data: Union[Dict[str, Any], List[Any], None] = None, params: Union[Dict[str, Any], None] = None) -> requests.Response:
        """
        Патч-запрос
        @param path_suffix: Суффикс, добавляемый после self.api_url
        @param headers: Хэдеры
        @param params: Кьюери-параметры
        @param data: - Боди (джсон)
        @return: Ответ внешнего сервиса
        """
        return self.make_request(self.METHODS.PATCH, path_suffix=path_suffix, headers=headers, data=data, params=params)

    def delete(self, path_suffix: str, headers: Union[Dict[str, Any], None] = None,
            data: Union[Dict[str, Any], List[Any], None] = None, params: Union[Dict[str, Any], None] = None) -> requests.Response:
        """
        Делет-запрос
        @param path_suffix: Суффикс, добавляемый после self.api_url
        @param headers: Хэдеры
        @param params: Кьюери-параметры
        @param data: - Боди (джсон)
        @return: Ответ внешнего сервиса
        """
        return self.make_request(self.METHODS.DELETE, path_suffix=path_suffix, headers=headers, data=data, params=params)
