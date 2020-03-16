from rest_framework import status
from rest_framework.views import APIView, Response, Request
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from Places.permissions import IsAuthenticated, IsModerator, IsSuperuser, CreateOnlyBySuperuser, UpdateOnlyBySuperuser
from Places.serializers import AcceptSerializer, RatingSerializer, PlaceImageSerializer, PlaceListSerializer, \
    PlaceDetailSerializer
from Places.models import Accept, Rating, PlaceImage, Place
from ApiRequesters.Auth.AuthRequester import AuthRequester
from ApiRequesters.utils import get_token_from_request


class AcceptsListView(ListCreateAPIView):
    """
    Вьюха для просмотра списка подтверждений
    """
    serializer_class = AcceptSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        with_deleted = self.request.query_params.get('show_deleted', False) and \
                       AuthRequester().is_superuser(get_token_from_request(self.request))
        place_id = self.request.query_params.get('place_id', None)
        if place_id is None:
            return Accept.objects.filter(deleted_flg__in=[False, with_deleted])
        else:
            return Accept.objects.filter(deleted_flg__in=[False, with_deleted], place_id=place_id)


class AcceptDetailView(RetrieveDestroyAPIView):
    """
    Вьюха для получения и удаления определенного подтверждения
    """
    serializer_class = AcceptSerializer
    permission_classes = (IsAuthenticated, )

    def perform_destroy(self, instance: Accept):
        instance.deleted_flg = True
        instance.save()
