from decimal import Decimal

from gym_management.tasks import (send_email_join_success_task,
                                  send_email_leave_success_task)
from users.models import Schedule


# AddOrRemoveParticipantService
def remove_user_from_event(event, user):
    event.participants.remove(user)
    user.balance += event.price
    user.save()
    event.save()
    send_email_leave_success_task.delay(user.email, user.first_name, event.id)


def add_user_to_event(event, user):
    event.participants.add(user)
    user.balance -= event.price
    user.save()
    event.save()
    send_email_join_success_task.delay(user.email, user.first_name, event.id)


# Уменьшение баланса
def down_user_balance(user, price):
    user.balance -= Decimal(price)
    user.save()


def change_time_selected(time, coach_id):
    from users.models import User
    coach = User.objects.get(id=coach_id)
    schedule = Schedule.objects.get(time=time, coach=coach)
    schedule.is_selected = True
    schedule.save()
