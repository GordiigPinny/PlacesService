from rest_framework import serializers
from Places.models import Place, Accept, Rating, PlaceImage
from ApiRequesters.Media.MediaRequester import MediaRequester
from ApiRequesters.utils import get_token_from_request
from ApiRequesters.exceptions import BaseApiRequestError


class PlaceImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор картинки места
    """
    created_dt = serializers.DateTimeField(read_only=True)
    deleted_flg = serializers.BooleanField(required=False)
    place_id = serializers.PrimaryKeyRelatedField(source='place', queryset=Place.objects.with_deleted().all())
    pic_id = serializers.IntegerField(min_value=1, required=True, allow_null=False)
    created_by = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = PlaceImage
        fields = [
            'id',
            'created_by',
            'place_id',
            'pic_id',
            'created_dt',
            'deleted_flg'
        ]

    def validate_pic_id(self, value: int):
        r = MediaRequester()
        token = get_token_from_request(self.context['request'])
        try:
            _ = r.get_image_info(value, token)
            return value
        except BaseApiRequestError:
            raise serializers.ValidationError('Валидация на поле pic_id свалилась, проверьте его, либо попропуйте позже')

    def create(self, validated_data):
        new = PlaceImage.objects.create(**validated_data)
        return new

    def update(self, instance: PlaceImage, validated_data):
        validated_data.pop('created_by')
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class RatingSerializer(serializers.ModelSerializer):
    """
    Сериализатор рейтинга
    """
    rating = serializers.IntegerField(min_value=0, max_value=5, required=True)
    created_dt = serializers.DateTimeField(read_only=True)
    deleted_flg = serializers.BooleanField(required=False)
    place_id = serializers.PrimaryKeyRelatedField(source='place', queryset=Place.objects.with_deleted().all())
    current_rating = serializers.FloatField(read_only=True, source='place.rating')
    created_by = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = PlaceImage
        fields = [
            'id',
            'created_by',
            'place_id',
            'rating',
            'current_rating',
            'created_dt',
            'deleted_flg'
        ]

    def create(self, validated_data):
        try:
            place_id, created_by = validated_data['place'].id, validated_data['created_by']
            rt = Rating.objects\
                .get(place_id=place_id, created_by=created_by)
            rt.soft_delete()
        except Rating.DoesNotExist:
            pass
        new = Rating.objects.create(**validated_data)
        return new

    def update(self, instance: Rating, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class AcceptSerializer(serializers.ModelSerializer):
    """
    Сериализатор подтверждения места
    """
    created_dt = serializers.DateTimeField(read_only=True)
    deleted_flg = serializers.BooleanField(required=False)
    place_id = serializers.PrimaryKeyRelatedField(source='place', queryset=Place.objects.with_deleted().all())
    created_by = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = Accept
        fields = [
            'id',
            'created_by',
            'place_id',
            'created_dt',
            'deleted_flg'
        ]

    def create(self, validated_data):
        place_id, created_by = validated_data['place'].id, validated_data['created_by']
        if Accept.objects.filter(created_by=created_by, place_id=place_id).exists():
            raise serializers.ValidationError('Вы уже подтвердили существование этого места')
        new = Accept.objects.create(**validated_data)
        return new

    def update(self, instance: Accept, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class PlaceListSerializer(serializers.ModelSerializer):
    """
    Сериализатор спискового представления места
    """
    deleted_flg = serializers.BooleanField(required=False)
    accept_type = serializers.SerializerMethodField()
    accepts_cnt = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_created_by_me = serializers.SerializerMethodField()
    created_by = serializers.IntegerField(min_value=1, write_only=True, required=True)

    class Meta:
        model = Place
        fields = [
            'id',
            'name',
            'latitude',
            'longitude',
            'address',
            'checked_by_moderator',
            'rating',
            'accept_type',
            'accepts_cnt',
            'deleted_flg',
            'created_by',
            'is_created_by_me',
        ]

    def get_accept_type(self, instance: Place):
        return instance.accept_type

    def get_accepts_cnt(self, instance: Place):
        return instance.accepts_cnt

    def get_rating(self, instance: Place):
        return instance.rating

    def get_is_created_by_me(self, instance: Place):
        try:
            user_id = self.context['request'].query_params['user_id']
            return instance.created_by == user_id
        except KeyError:
            return False

    def create(self, validated_data):
        new = Place.objects.create(**validated_data)
        return new


class PlaceDetailSerializer(PlaceListSerializer):
    """
    Сериализатор детального представления места
    """
    created_dt = serializers.DateTimeField(read_only=True)
    my_rating = serializers.SerializerMethodField()
    is_accepted_by_me = serializers.SerializerMethodField()
    created_by = serializers.IntegerField(min_value=1, read_only=True)

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + [
            'created_dt',
            'my_rating',
            'is_accepted_by_me',
        ]

    def get_my_rating(self, instance: Place):
        try:
            user_id = self.context['request'].query_params['user_id']
            return Rating.objects.get(place_id=instance.id, created_by=user_id)
        except (KeyError, Rating.DoesNotExist):
            return 0

    def get_is_accepted_by_me(self, instance: Place):
        try:
            user_id = self.context['request'].query_params['user_id']
            return Accept.objects.filter(place_id=instance.id, created_by=user_id).exists()
        except KeyError:
            return False

    def update(self, instance: Place, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
