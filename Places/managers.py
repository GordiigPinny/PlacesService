from django.db.models import Manager


class PlacesManager(Manager):
    """
    ORM менеджер для мест
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_flg=False)

    def with_deleted(self):
        return super().get_queryset()


class AcceptsManager(Manager):
    """
    ORM менеджер для подтверждений
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_flg=False)

    def with_deleted(self):
        return super().get_queryset()


class RatingsManager(Manager):
    """
    ORM менеджер для рейтинга
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_flg=False)

    def with_deleted(self):
        return super().get_queryset()


class PlaceImagesManager(Manager):
    """
    ORM менеджер для фото мест
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_flg=False)

    def with_deleted(self):
        return super().get_queryset()
