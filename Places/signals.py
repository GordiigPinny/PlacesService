from django.db.models.signals import post_save
from django.dispatch import receiver
from Places.models import Place


@receiver(post_save, sender=Place)
def delete_all_after_place(sender, instance: Place, created, update_fields, **kwargs):
    """
    Установка deleted_flg у всех связанных сущностей с мягкоудоляемым местом
    """
    if created:
        return
    if 'deleted_flg' not in update_fields:
        return
    for accept in instance.accepts.all():
        accept.deleted_flg = True
        accept.save()
    for rating in instance.ratings.all():
        rating.deleted_flg = True
        rating.save()
    for img in instance.images.all():
        img.deleted_flg = True
        img.save()
