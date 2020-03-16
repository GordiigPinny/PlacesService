from django.conf import settings
from ._AuthRequester import AuthRequester as __a, MockAuthRequester as __m

__tst = settings.TESTING
try:
    __ar = settings.ALLOW_REQUESTS
    AuthRequester = __a if __ar and not __tst else __m
except AttributeError:
    AuthRequester = __a if not __tst else __m
