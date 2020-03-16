from rest_framework.permissions import BasePermission
from ApiRequesters.Auth.permissions import IsAuthenticated, IsModerator, IsSuperuser
from ApiRequesters.Auth.AuthRequester import AuthRequester
from ApiRequesters.utils import get_token_from_request


class CreateOnlyBySuperuser(BasePermission):
    """
    Пермишн на создание объектов только суперюзером
    """
    message = 'Only superuser can create new instances'

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        return AuthRequester().is_superuser(get_token_from_request(request))


class UpdateOnlyBySuperuser(BasePermission):
    """
    Пермишн на обновление объектов только суперюзером
    """
    message = 'Only superuser can update instances'

    def has_permission(self, request, view):
        if request.method != 'PATCH':
            return True
        return AuthRequester().is_superuser(get_token_from_request(request))
