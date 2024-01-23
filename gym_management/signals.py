from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from gym_management.models import Subscription
from gym_management.tasks import (
    send_email_join_success_task,
    send_email_leave_success_task,
)

from .models import Event


@receiver(post_save, sender=Subscription)
def add_end_date(sender, instance, created, **kwargs):
    if created:
        instance.end_date = instance.calculate_end_date()
        instance.save()


# @receiver(pre_save, sender=Event)
# def send_join_leave_email(sender, instance, update_fields, **kwargs):
#     if "participants" in update_fields:
#         event = instance
#         old_participants_count = len(instance._old_values.get("participants", []))
#         new_participants_count = len(instance.participants.all())

#         if new_participants_count > old_participants_count:
#             # Добавлен новый участник
#             added_participant = event.participants.exclude(
#                 id__in=instance._old_values.get("participants", [])
#             ).first()

#             # Теперь added_participant содержит нового участника, если таковой был добавлен
#             if added_participant:
#                 send_email_join_success_task.delay(added_participant, event)
#         elif new_participants_count < old_participants_count:
#             # Удален участник
#             removed_participant = instance._old_values.get("participants", []).first()

#             # Теперь removed_participant содержит удаленного участника, если таковой был удален
#             if removed_participant:
#                 send_email_leave_success_task.delay(removed_participant, event)
