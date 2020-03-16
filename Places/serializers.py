from rest_framework import serializers
from Places.models import Place, Accept, Rating, PlaceImage


class PlaceImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор картинки места
    """
    created_dt = serializers.DateTimeField(read_only=True)
    deleted_flg = serializers.BooleanField(required=False)

    class Meta:
        model = PlaceImage
        fields = [
            'id',
            'created_by',
            'place_id',
            'pic_link',
            'created_dt',
            'deleted_flg'
        ]

    def create(self, validated_data):
        new = PlaceImage.objects.create(**validated_data)
        return new

    def update(self, instance: PlaceImage, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class RatingSerializer(serializers.ModelSerializer):
    """
    Сериализатор рейтинга
    """
    rating = serializers.IntegerField(min_value=0, max_value=5)
    created_dt = serializers.DateTimeField(read_only=True)
    deleted_flg = serializers.BooleanField(required=False)

    class Meta:
        model = PlaceImage
        fields = [
            'id',
            'created_by',
            'place_id',
            'rating',
            'created_dt',
            'deleted_flg'
        ]

    def create(self, validated_data):
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
        ]

    def get_accept_type(self, instance: Place):
        return instance.accept_type

    def get_accepts_cnt(self, instance: Place):
        return instance.accepts_cnt

    def get_rating(self, instance: Place):
        return instance.rating

    def create(self, validated_data):
        new = Place.objects.create(**validated_data)
        return new


class PlaceDetailSerializer(PlaceListSerializer):
    """
    Сериализатор детального представления места
    """
    created_dt = serializers.DateTimeField(read_only=True)

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + [
            'created_dt',
        ]

    def update(self, instance: Place, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
