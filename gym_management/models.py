from collections.abc import Iterable

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from users.models import User


class Tag(models.Model):
    """Model for tags"""

    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"Тег: {self.name}"


class Club(models.Model):
    """Model for clubs"""

    address = models.CharField(max_length=256)
    club_phone = PhoneNumberField()
    club_email = models.EmailField()
    coaches = models.ManyToManyField(User)

    class Meta:
        verbose_name = "клуб"
        verbose_name_plural = "Клубы"

    def __str__(self):
        return f"Клуб: {self.address}"


class Event(models.Model):
    """Model for events"""

    WAITING = "waiting"
    CANCELED = "canceled"
    PASSED = "passed"

    STATUS_CHOICES = (
        (WAITING, "Waiting"),
        (CANCELED, "Canceled"),
        (PASSED, "Passed"),
    )

    title = models.CharField(max_length=128)
    content = models.TextField()
    participants = models.ManyToManyField(User, related_name="participants_event")
    limit_of_participants = models.SmallIntegerField()
    tags = models.ManyToManyField(Tag)
    start_date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.CharField(max_length=150)
    price = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WAITING)

    class Meta:
        verbose_name = "тренировку"
        verbose_name_plural = "Тренировки"

    def __str__(self):
        return f"Тренировка: {self.title} | {self.created_by}"
    
    def seats_left(self):
        return self.limit_of_participants - self.participants.count()


class IndividualEvent(models.Model):
    """Model for individual events"""

    coach = models.ForeignKey(
        User, related_name="coach_events", on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        User, related_name="participant_events", on_delete=models.CASCADE
    )
    training_date = models.DateTimeField(unique=True)
    description = models.TextField(default="Personal training")
    duration = models.PositiveIntegerField(default=0)
    quantity = models.IntegerField(default=1)
    price = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "индивидуальную тренировку"
        verbose_name_plural = "Индивидуальные тренировки"
        constraints = [
            models.UniqueConstraint(
                fields=["coach", "participant"], name="unique_coach_participant"
            )
        ]

    def __str__(self) -> str:
        return f"Individual event with {self.participant.first_name} on {self.training_date} at {self.duration}"

    def clean(self):
        # Дополнительная проверка на уровне модели
        if IndividualEvent.objects.filter(
            coach=self.coach, participant=self.participant
        ).exists():
            raise ValidationError(
                _("This combination of coach and participant already exists.")
            )


class Subscription(models.Model):
    """Model for subscription"""

    number = models.BigIntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "aбонемент"
        verbose_name_plural = "абонементы"

    def __str__(self) -> str:
        return f"Subscription: number {self.number} | user {self.user} | duration {self.duration}"

    def calculate_end_date(self):
        return self.start_date + timezone.timedelta(days=int(self.duration))
