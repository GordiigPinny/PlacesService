from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from Places.serializers import AcceptSerializer, RatingSerializer, PlaceImageSerializer, PlaceListSerializer, \
    PlaceDetailSerializer
from Places.models import Accept, Rating, PlaceImage, Place
from Places.permissions import WriteOnlyBySuperuser, WriteOnlyByModerator, WriteOnlyByAuthenticated
from ApiRequesters.Auth.permissions import IsAuthenticated
from ApiRequesters.Auth.AuthRequester import AuthRequester
from ApiRequesters.utils import get_token_from_request
from ApiRequesters.exceptions import BaseApiRequestError
from ApiRequesters.Stats.decorators import collect_request_stats_decorator, CollectStatsMixin
from ApiRequesters.Stats.StatsRequester import StatsRequester


class BaseListCreateView(ListCreateAPIView, CollectStatsMixin):
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

    @collect_request_stats_decorator()
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BaseRetrieveDestroyView(RetrieveDestroyAPIView, CollectStatsMixin):
    """
    Базовый класс для RetriveDestroy для Accept, Rating, PlaceImage
    """
    model_class = None

    def get_queryset(self):
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        return self.model_class.objects.with_deleted().all() if with_deleted else self.model_class.objects.all()

    @collect_request_stats_decorator()
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @collect_request_stats_decorator()
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class AcceptsListView(BaseListCreateView):
    """
    Вьюха для просмотра списка подтверждений
    """
    model_class = Accept
    permission_classes = (IsAuthenticated, )
    serializer_class = AcceptSerializer
    pagination_class = LimitOffsetPagination

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_accept_stats])
    def post(self, request, *args, **kwargs):
        self.additional_kwargs_for_stats_funcs = []
        serializer = self.get_serializer(data=request.data)
        add_kwargs = []
        if serializer.is_valid():
            add_kwargs.append({
                'action': StatsRequester.ACCEPTS_ACTIONS.ACCEPTED,
                'place_id': request.data['place_id'],
                'request': request,
            })
        return super().post(request, *args, **kwargs)


class AcceptDetailView(BaseRetrieveDestroyView):
    """
    Вьюха для получения и удаления определенного подтверждения
    """
    model_class = Accept
    permission_classes = (IsAuthenticated, )
    serializer_class = AcceptSerializer


class RatingsListView(BaseListCreateView):
    """
    Вьюха для просмотра списка рейтингов
    """
    model_class = Rating
    permission_classes = (IsAuthenticated, )
    serializer_class = RatingSerializer
    pagination_class = LimitOffsetPagination

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_rating_stats])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        add_kwargs = []
        if serializer.is_valid():
            add_kwargs.append({
                'old_rating': Rating.objects.get(created_by=serializer['created_by'].value,
                                                 place_id=request.data['place_id']).rating,
                'new_rating': request.data['rating'],
                'place_id': request.data['place_id'],
                'request': request,
            })
        return super().post(request, *args, **kwargs), add_kwargs


class RatingDetailView(BaseRetrieveDestroyView):
    """
    Вьюха для получения и удаления рейтинга
    """
    model_class = Rating
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer


class PlaceImagesListView(BaseListCreateView):
    """
    Вьюха для получения списка изображений места
    """
    model_class = PlaceImage
    permission_classes = (WriteOnlyByModerator, )
    serializer_class = PlaceImageSerializer
    pagination_class = LimitOffsetPagination

    @collect_request_stats_decorator()
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PlaceImageDetailView(BaseRetrieveDestroyView):
    """
    Вьюха для получения и удаления картинки места
    """
    model_class = PlaceImage
    permission_classes = (WriteOnlyByModerator,)
    serializer_class = PlaceImageSerializer


class PlacesListView(ListCreateAPIView, CollectStatsMixin):
    """
    Вьюха для получения списка мест
    """
    permission_classes = (WriteOnlyByAuthenticated, )
    serializer_class = PlaceListSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        lookup_fields = {}
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        all_ = Place.objects.with_deleted() if with_deleted else Place.objects

        only_mine = self.request.query_params.get('only_mine', 'False')
        only_mine = only_mine.lower() == 'true'
        if only_mine:
            r = AuthRequester()
            token = get_token_from_request(self.request)
            try:
                _, auth_json = r.get_user_info(token)
                lookup_fields['created_by'] = auth_json['id']
            except BaseApiRequestError:
                raise ValidationError('Не получается получить юзера по токену, попробуйте позже')

        latitude_1 = self.request.query_params.get('lat1', None)
        longitude_1 = self.request.query_params.get('long1', None)
        latitude_2 = self.request.query_params.get('lat2', None)
        longitude_2 = self.request.query_params.get('long2', None)
        llll = (latitude_1, latitude_2, longitude_1, longitude_2)
        if all(llll):
            try:
                lookup_fields['latitude__gte'] = min(float(latitude_1), float(latitude_2))
                lookup_fields['longitude__gte'] = min(float(longitude_1), float(longitude_2))
                lookup_fields['latitude__lte'] = max(float(latitude_1), float(latitude_2))
                lookup_fields['longitude__lte'] = max(float(longitude_1), float(longitude_2))
            except (ValueError, TypeError):
                raise ValidationError('Для фильтрации по сектору карты параметры должны быть числами')
        elif len(list(filter(lambda x: x is not None, llll))) != 0:
            raise ValidationError('Для фильтрации по сектору карты нужны 4 координаты')
        return all_.filter(**lookup_fields)

    @collect_request_stats_decorator()
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_place_stats])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        add_kwargs = []
        if serializer.is_valid():
            add_kwargs.append({
                'action': StatsRequester.PLACES_ACTIONS.CREATED,
                'request': request,
            })
        resp = super().post(request, *args, **kwargs)
        if resp.status_code == 201:
            add_kwargs[0]['place_id'] = resp.data['id']
        return resp, add_kwargs


class PlaceDetailView(RetrieveUpdateDestroyAPIView, CollectStatsMixin):
    """
    Вьюха для получения, изменения и удаления места
    """
    permission_classes = (WriteOnlyBySuperuser, )
    serializer_class = PlaceDetailSerializer

    def get_queryset(self):
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        return Place.objects.with_deleted().all() if with_deleted else Place.objects.all()

    def perform_destroy(self, instance: Place):
        instance.soft_delete()

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_place_stats])
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        add_kwargs = []
        if serializer.is_valid():
            add_kwargs.append({
                'action': StatsRequester.PLACES_ACTIONS.OPENED,
                'place_id': self.kwargs['pk'],
                'request': request,
            })
        return super().get(request, *args, **kwargs), add_kwargs

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_place_stats])
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        add_kwargs = []
        if serializer.is_valid():
            add_kwargs.append({
                'action': StatsRequester.PLACES_ACTIONS.EDITED,
                'place_id': self.kwargs['pk'],
                'request': request,
            })
        response = super().update(request, args, kwargs)
        if response.status_code == 200:
            response.status_code = 202
        return response, add_kwargs

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_place_stats])
    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        add_kwargs = []
        if serializer.is_valid():
            add_kwargs.append({
                'action': StatsRequester.PLACES_ACTIONS.DELETED,
                'place_id': self.kwargs['pk'],
                'request': request,
            })
        return super().delete(request, *args, **kwargs), add_kwargs
