import json
from ApiRequesters.Mock.MockRequesterMixin import MockRequesterMixin


class TestToken:
    """
    Базовый класс для токена, использующегося в тестах
    Представляет собой просто строку -- настоящий токен
    """
    ERRORS_KEYS = MockRequesterMixin.ERRORS_KEYS
    ERRORS = MockRequesterMixin.ERRORS
    ROLES = MockRequesterMixin.ROLES

    def __init__(self, token, prefix: str = 'Bearer'):
        self.prefix = prefix
        self._token = token

    @property
    def token(self):
        return self.prefix + ' ' + self._token

    def set_error(self, service: MockRequesterMixin.ERRORS_KEYS, error: MockRequesterMixin.ERRORS):
        pass

    def set_role(self, role: MockRequesterMixin.ROLES):
        pass

    def set_another_key(self, key: str, val: str):
        pass

    def set_authenticate(self, val: bool):
        pass


class TestMockToken(TestToken):
    """
    Токен для мок-тестов
    Токен -- словарь, подходящий к мок-тестам
    """
    def __init__(self, token=None):
        token = {x.value: '' for x in self.ERRORS_KEYS}
        token['role'] = self.ROLES.USER.value
        token['authenticate'] = True
        super().__init__(token=token)

    @property
    def token(self):
        return json.dumps(self._token)

    def set_error(self, service: MockRequesterMixin.ERRORS_KEYS, error: MockRequesterMixin.ERRORS):
        self._token[service.value] = error.value

    def set_role(self, role: MockRequesterMixin.ROLES):
        self._token['role'] = role.value

    def set_another_key(self, key: str, val: str):
        self._token[key] = val

    def set_authenticate(self, val: bool):
        self._token['authenticate'] = val
