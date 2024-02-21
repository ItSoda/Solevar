from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from gym_management.models import Event, IndividualEvent, Subscription

from .tasks import send_email_canceled_event


@receiver(post_save, sender=Subscription)
def add_end_date(sender, instance, **kwargs):
    instance.end_date = instance.calculate_end_date()
    Subscription.objects.filter(pk=instance.pk).update(end_date=instance.end_date)


@receiver(post_save, sender=IndividualEvent)
def check_quantity_individual_events(sender, instance, **kwargs):
    if instance.quantity == 0:
        instance.delete()


@receiver(post_save, sender=Event)
def check_quantity_individual_events(sender, instance, **kwargs):
    if instance.status == Event.CANCELED:
        participants_ids = instance.participants.all().values_list("id", flat=True)
        title = instance.title
        send_email_canceled_event.delay(list(participants_ids), title)
