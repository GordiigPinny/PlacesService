from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from Places.serializers import AcceptSerializer, RatingSerializer, PlaceImageSerializer, PlaceListSerializer, \
    PlaceDetailSerializer
from Places.models import Accept, Rating, PlaceImage, Place


class BaseListCreateView(ListCreateAPIView):
    """
    Базовый класс для ListCreate для Accept, Rating, PlaceImage
    """
    model_class = None

    def get_queryset(self):
        place_id = self.request.query_params.get('place_id', None)
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        all_ = self.model_class.objects.with_deleted() if with_deleted else self.model_class.objects
        if place_id is None:
            return all_.all()
        else:
            return all_.filter(place_id=place_id)


class BaseRetrieveDestroyView(RetrieveDestroyAPIView):
    """
    Базовый класс для RetriveDestroy для Accept, Rating, PlaceImage
    """
    model_class = None

    def get_queryset(self):
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        return self.model_class.objects.with_deleted().all() if with_deleted else self.model_class.objects.all()

    def perform_destroy(self, instance):
        instance.soft_delete()


class AcceptsListView(BaseListCreateView):
    """
    Вьюха для просмотра списка подтверждений
    """
    model_class = Accept
    serializer_class = AcceptSerializer
    pagination_class = LimitOffsetPagination


class AcceptDetailView(BaseRetrieveDestroyView):
    """
    Вьюха для получения и удаления определенного подтверждения
    """
    model_class = Accept
    serializer_class = AcceptSerializer


class RatingsListView(BaseListCreateView):
    """
    Вьюха для просмотра списка рейтингов
    """
    model_class = Rating
    serializer_class = RatingSerializer
    pagination_class = LimitOffsetPagination


class RatingDetailView(BaseRetrieveDestroyView):
    """
    Вьюха для получения и удаления рейтинга
    """
    model_class = Rating
    serializer_class = RatingSerializer


class PlaceImagesListView(BaseListCreateView):
    """
    Вьюха для получения списка изображений места
    """
    model_class = PlaceImage
    serializer_class = PlaceImageSerializer
    pagination_class = LimitOffsetPagination


class PlaceImageDetailView(BaseRetrieveDestroyView):
    """
    Вьюха для получения и удаления картинки места
    """
    model_class = PlaceImage
    serializer_class = PlaceImageSerializer


class PlacesListView(ListCreateAPIView):
    """
    Вьюха для получения списка мест
    """
    serializer_class = PlaceListSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        lookup_fields = {}
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        all_ = Place.objects.with_deleted() if with_deleted else Place.objects
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
        return all_.filter(**lookup_fields)


class PlaceDetailView(RetrieveUpdateDestroyAPIView):
    """
    Вьюха для получения, изменения и удаления места
    """
    serializer_class = PlaceDetailSerializer

    def get_queryset(self):
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        return Place.objects.with_deleted().all() if with_deleted else Place.objects.all()

    def update(self, request, *args, **kwargs):
        response = super().update(request, args, kwargs)
        if response.status_code == 200:
            response.status_code = 202
        return response

    def perform_destroy(self, instance: Place):
        instance.soft_delete()
