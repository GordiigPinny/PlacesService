from django.db import models


class Place(models.Model):
    """
    Модель места
    """
    name = models.CharField(max_length=512, null=False, blank=False)
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False)
    address = models.CharField(max_length=512, null=False, blank=False)
    checked_by_moderator = models.BooleanField(default=False)
    created_by = models.PositiveIntegerField(null=False, blank=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)

    @property
    def rating(self) -> float:
        ratings_vals = [x.rating for x in self.ratings]
        return sum(ratings_vals) / len(ratings_vals) if len(ratings_vals) != 0 else 0.0

    @property
    def accepts_cnt(self):
        return self.accepts.count()

    @property
    def accept_type(self):
        cnt = self.accepts_cnt
        if cnt < 50:
            return 'Непроверенное место'
        elif 50 <= cnt < 100:
            return 'Слабо проверенное место'
        elif 100 <= cnt < 200:
            return 'Проверенное многими место'
        else:
            return 'Проверенное место'

    def soft_delete(self):
        self.deleted_flg = True
        self.save(update_fields=['deleted_flg'])

    def __str__(self):
        return f'Place {self.name}'


class Accept(models.Model):
    """
    Модель для одобрения выложенного места
    """
    created_by = models.PositiveIntegerField(null=False, blank=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='accepts')
    created_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)

    def __str__(self):
        return f'Accept({self.id}) by {self.created_by}, on place {self.place.id}'


class Rating(models.Model):
    """
    Модель рейтинга, который юзер дает месту
    """
    created_by = models.PositiveIntegerField(null=False, blank=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(null=False, blank=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)


class PlaceImage(models.Model):
    """
    Модель картинки места
    """
    created_by = models.PositiveIntegerField(null=False, blank=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    pic_link = models.URLField(null=False, blank=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)
