from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from gym_management.models import Subscription


@receiver(post_save, sender=Subscription)
def add_end_date(sender, instance, **kwargs):
    instance.end_date = instance.calculate_end_date()
    Subscription.objects.filter(pk=instance.pk).update(end_date=instance.end_date)
