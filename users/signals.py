from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Storages, Users


# when User Create, Storage Create
@receiver(post_save, sender=Users)
def Users_post_save(sender, created, **kwargs):
    if created and kwargs['update_fields'] is None:
        storage = Storages.objects.create(email=kwargs['instance'])
        storage.save()
