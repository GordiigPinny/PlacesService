from rest_framework.permissions import BasePermission, SAFE_METHODS
from ApiRequesters.Auth.permissions import IsModerator, IsSuperuser, IsAuthenticated


class WriteOnlyByAuthenticated(BasePermission):
    """
    Пермишн на запись только зарегистрированными
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsAuthenticated().has_permission(request, view)


class WriteOnlyByModerator(BasePermission):
    """
    Пермишн на запись только модераторами
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsModerator().has_permission(request, view)


class WriteOnlyBySuperuser(BasePermission):
    """
    Пермишн на запись только суперюзерами
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsSuperuser().has_permission(request, view)
