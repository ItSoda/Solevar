from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
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

    title = models.CharField(max_length=128)
    content = models.TextField()
    participants = models.ManyToManyField(User, related_name="participants_event")
    limit_of_participants = models.SmallIntegerField()
    tags = models.ManyToManyField(Tag)
    start_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "тренировку"
        verbose_name_plural = "Тренировки"

    def __str__(self):
        return f"Тренировка: {self.title} | {self.created_by}"


class IndividualEvent(models.Model):
    """Model for individual events"""

    coach = models.ForeignKey(
        User, related_name="coach_events", on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        User, related_name="participant_events", on_delete=models.CASCADE
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField()
    duration = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "индивидуальную тренировку"
        verbose_name_plural = "Индивидуальные тренировки"
        constraints = [
            models.UniqueConstraint(fields=['coach', 'participant'], name='unique_coach_participant')
        ]

    def __str__(self) -> str:
        return f"Individual event with {self.participant.first_name} on {self.start_datetime} at {self.duration}"
    
    def clean(self):
        # Дополнительная проверка на уровне модели
        if IndividualEvent.objects.filter(coach=self.coach, participant=self.participant).exists():
            raise ValidationError(_('This combination of coach and participant already exists.'))


class Subscription(models.Model):
    """Model for subscription"""

    number = models.BigIntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "aбонемент"
        verbose_name_plural = "абонементы"

    def __str__(self) -> str:
        return f"Subscription: number {self.number} | user {self.user} | end_date {self.duration}"
