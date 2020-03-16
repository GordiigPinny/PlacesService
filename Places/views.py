from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView, Response, Request
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from Places.permissions import IsAuthenticated, IsModerator, IsSuperuser, CreateOnlyBySuperuser, UpdateOnlyBySuperuser, \
    DeleteOnlyBySuperuser
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

    def get_queryset(self):
        with_deleted = self.request.query_params.get('show_deleted', False) and \
                       AuthRequester().is_superuser(get_token_from_request(self.request))
        return Accept.objects.filter(deleted_flg__in=[with_deleted, False])

    def perform_destroy(self, instance: Accept):
        instance.deleted_flg = True
        instance.save()


class RatingsListView(ListCreateAPIView):
    """
    Вьюха для просмотра списка рейтингов
    """
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        with_deleted = self.request.query_params.get('show_deleted', False) and \
                       AuthRequester().is_superuser(get_token_from_request(self.request))
        place_id = self.request.query_params.get('place_id', None)
        if place_id is None:
            return Rating.objects.filter(deleted_flg__in=[False, with_deleted])
        else:
            return Rating.objects.filter(deleted_flg__in=[False, with_deleted], place_id=place_id)


class RatingDetailView(RetrieveDestroyAPIView):
    """
    Вьюха для получения и удаления рейтинга
    """
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        with_deleted = self.request.query_params.get('show_deleted', False) and \
                       AuthRequester().is_superuser(get_token_from_request(self.request))
        return Rating.objects.filter(deleted_flg__in=[with_deleted, False])

    def perform_destroy(self, instance: Rating):
        instance.deleted_flg = True
        instance.save()


class PlaceImagesListView(ListCreateAPIView):
    """
    Вьюха для получения списка изображений места
    """
    serializer_class = PlaceImageSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        with_deleted = self.request.query_params.get('show_deleted', False) and \
                       AuthRequester().is_superuser(get_token_from_request(self.request))
        place_id = self.request.query_params.get('place_id', None)
        if place_id is None:
            return PlaceImage.objects.filter(deleted_flg__in=[False, with_deleted])
        else:
            return PlaceImage.objects.filter(deleted_flg__in=[False, with_deleted], place_id=place_id)


class PlaceImageDetailView(RetrieveDestroyAPIView):
    """
    Вьюха для получения и удаления картинки места
    """
    serializer_class = PlaceImageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        with_deleted = self.request.query_params.get('show_deleted', False) and \
                       AuthRequester().is_superuser(get_token_from_request(self.request))
        return PlaceImage.objects.filter(deleted_flg__in=[with_deleted, False])

    def perform_destroy(self, instance: PlaceImage):
        instance.deleted_flg = True
        instance.save()


class PlacesListView(ListCreateAPIView):
    """
    Вьюха для получения списка мест
    """
    serializer_class = PlaceListSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        lookup_fields = {}
        lookup_fields['deleted_flg__in'] = [self.request.query_params.get('show_deleted', False) and
                                            AuthRequester().is_superuser(get_token_from_request(self.request)), False]
        latitude_1 = self.request.query_params.get('latitude_1', None)
        longitude_1 = self.request.query_params.get('longitude_1', None)
        latitude_2 = self.request.query_params.get('latitude_2', None)
        longitude_2 = self.request.query_params.get('longitude_2', None)
        llll = (latitude_1, latitude_2, longitude_1, longitude_2)
        if all(llll):
            lookup_fields['latitude__gte'] = min(latitude_1, latitude_2)
            lookup_fields['longitude__gte'] = min(longitude_1, longitude_2)
            lookup_fields['latitude__lte'] = max(latitude_1, latitude_2)
            lookup_fields['longitude__lte'] = max(longitude_1, longitude_2)
        elif len(list(filter(lambda x: x is not None, llll))) != 0:
            raise ValidationError({'error': 'You need to write all 4 coords for area filtering'})
        return Place.objects.filter(**lookup_fields)


class PlaceDetailView(RetrieveUpdateDestroyAPIView):
    """
    Вьюха для получения, изменения и удаления места
    """
    serializer_class = PlaceDetailSerializer
    permission_classes = (IsAuthenticated, UpdateOnlyBySuperuser, DeleteOnlyBySuperuser)

    def get_queryset(self):
        with_deleted = self.request.query_params.get('show_deleted', False) and \
                       AuthRequester().is_superuser(get_token_from_request(self.request))
        return Place.objects.filter(deleted_flg__in=[with_deleted, False])

    def perform_destroy(self, instance: Place):
        instance.soft_delete()
