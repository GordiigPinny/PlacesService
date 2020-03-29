from typing import Type, Union, List, Dict, Any
from django.db.models import Model, QuerySet
from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth.models import User


class BaseTestCase(TestCase):
    def setUp(self):
        self.url_prefix = '/api/'
        self.user_username = 'Test'
        self.user_password = 'Test'
        self.user, _ = User.objects.get_or_create(username=self.user_username, password='')
        self.user.set_password(self.user_password)
        self.user.save()

    def _get_api_client(self, auth: bool) -> APIClient:
        client = APIClient()
        if auth:
            client.force_authenticate(user=self.user)
        return client

    def _handle_response(self, response, expected_status_code: int, url: str) -> dict:
        self.assertEqual(response.status_code, expected_status_code,
                         msg=f'Respone\'s status code for url {url} is {response.status_code}, '
                             f'expected {expected_status_code}')
        json_response = {}
        try:
            json_response = response.json()
        except TypeError:
            pass
        finally:
            return json_response

    def get_response_and_check_status(self, url: str, data: dict = {}, expected_status_code: int = 200,
                                      auth: bool = False, token: Union[str, None] = None):
        """
        GET-запрос на сервер с проверкой статус-кода
        :param url: Урла куда стучимся
        :param data: Что кладем в body
        :param expected_status_code: Ожидаемый код возврата
        :param auth: Нужно ли аутентифицироваться (тестовым юзером)
        :param token: Токен, если нужно тестить что-то с ним (юзать с auth = False)
        :return: JSON, который вернулся с сервера
        """
        client = self._get_api_client(auth)
        if token:
            assert not auth
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(url, data=data)
        json = self._handle_response(response, expected_status_code, url)
        return json

    def post_response_and_check_status(self, url: str, data: dict = {}, expected_status_code: int = 201,
                                       auth: bool = False, token: Union[str, None] = None):
        """
        POST-запрос на сервер с проверкой статус-кода
        :param url: Урла куда стучимся
        :param data: Что кладем в body
        :param expected_status_code: Ожидаемый код возврата
        :param auth: Нужно ли аутентифицироваться (тестовым юзером)
        :param token: Токен, если нужно тестить что-то с ним (юзать с auth = False)
        :return: JSON, который вернулся с сервера
        """
        client = self._get_api_client(auth)
        if token:
            assert not auth
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.post(url, data=data, format='json')
        json = self._handle_response(response, expected_status_code, url)
        return json

    def patch_response_and_check_status(self, url: str, data: dict = {}, expected_status_code: int = 202,
                                        auth: bool = False, token: Union[str, None] = None):
        """
        PATCH-запрос на сервер с проверкой статус-кода
        :param url: Урла куда стучимся
        :param data: Что кладем в body
        :param expected_status_code: Ожидаемый код возврата
        :param auth: Нужно ли аутентифицироваться (тестовым юзером)
        :param token: Токен, если нужно тестить что-то с ним (юзать с auth = False)
        :return: JSON, который вернулся с сервера
        """
        client = self._get_api_client(auth)
        if token:
            assert not auth
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.patch(url, data=data, format='json')
        json = self._handle_response(response, expected_status_code, url)
        return json

    def delete_response_and_check_status(self, url: str, data: dict = {}, expected_status_code: int = 204,
                                         auth: bool = False, token: Union[str, None] = None):
        """
        DELETE-запрос на сервер с проверкой статус-кода
        :param url: Урла куда стучимся
        :param data: Что кладем в body
        :param expected_status_code: Ожидаемый код возврата
        :param auth: Нужно ли аутентифицироваться (тестовым юзером)
        :param token: Токен, если нужно тестить что-то с ним (юзать с auth = False)
        :return: JSON, который вернулся с сервера
        """
        client = self._get_api_client(auth)
        if token:
            assert not auth
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.delete(url, data=data)
        json = self._handle_response(response, expected_status_code, url)
        return json

    def fields_test(self, response_json: Union[list, dict], needed_fields: List[str], allow_extra_fields: bool = True):
        """
        Проверка наличия необходимых полей в ответе сервера
        :param response_json: То, что вернул сервер
        :param needed_fields: Необходимые поля в каждом JSON-объекте
        :param allow_extra_fields Разрешаются ли в JSON-объекте поля, которых нет в needed_fields
        """
        if isinstance(response_json, dict):
            self._single_dict_field_test(response_json, needed_fields, allow_extra_fields)
        elif isinstance(response_json, list):
            for obj in response_json:
                self._single_dict_field_test(obj, needed_fields, allow_extra_fields)
        else:
            self.assertTrue(False, 'response_json has unexpected type')

    def _single_dict_field_test(self, obj: Dict[str, Any], needed_fields: List[str], allow_extra_fields: bool):
        """
        Собственно, сама проверка на наличие нужных полей (проверяется равенством множеств)
        :param obj: JSON-объект
        :param needed_fields: Необходимые поля
        :param allow_extra_fields Разрешаются ли в JSON-объекте поля, которых нет в needed_fields
        """
        keys = set(obj.keys())
        fields = set(needed_fields)
        # Если разрешаются дополнительные поля, то выбросим их из множества, чтобы не мешали при проверке на равенство
        if allow_extra_fields:
            extra = keys.difference(fields)
            keys = keys.difference(extra)
        if keys != fields:
            in_fields = fields.difference(keys)
            in_keys = keys.difference(fields)
            self.assertTrue(False, f'Response object\'s extra fields: {in_keys}, lack of fields: {in_fields}')

    def list_test(self, response_json: dict, mclass: Type[Model], field_for_lookup: str = 'id') -> QuerySet:
        """
        Базовый тест списка, который вернул сервер
        :param response_json: То, что вернул сервер
        :param mclass: Класс модели (не объект!), который был сериализован и возвращен сервером (возможно еще прикольней
            его можно использовать)
        :param field_for_lookup: Имя поля, по которому будет идти проверка на то, что все данные были переданы сервером
        :return Все объекты модели mclass, чтобы в бд еще раз не стучаться для дальнейших тестов
        """
        # Список ли это (тут может быть либо список, либо словарь, так что такая тупая проверка подойдет),
        # и если да, то заодно вытянем длинну
        try:
            resp_len = len(response_json)
        except TypeError:
            self.assertTrue(False, 'Response json is not a list -- can\'t take len() from it')
        all_objs = mclass.objects.all()
        actual_len = all_objs.count()
        # Проверяем все ли вернулось
        self.assertEqual(resp_len, actual_len, f'Response length is {resp_len}, but actual length is {actual_len}')
        # Для каждого объекта из бд ищем такой же в списке из респонза фильторванием, и если после фильтра пусто --
        # то такого объекта нет в респонзе
        for obj in all_objs:
            try:
                _ = list(filter(lambda x: x[field_for_lookup] == getattr(obj, field_for_lookup), response_json))[0]
            except IndexError:
                self.assertTrue(False,
                                f'Some objects are not in response json -- filtering by {field_for_lookup}'
                                f' returned empty list')
        return all_objs
