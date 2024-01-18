from django.db import models
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Tag(models.Model):
    name = models.CharField(max_length=64)
    
    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"Тег: {self.name}"


class Club(models.Model):
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
    title = models.CharField(max_length=128)
    content = models.TextField()
    participants = models.ManyToManyField(User, related_name="participants_event")
    limit_of_participants = models.SmallIntegerField()
    tags = models.ManyToManyField(Tag)
    start_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "тренировку"
        verbose_name_plural = "Тренировки"

    def __str__(self):
        return f"Тренировка: {self.title} | {self.created_by}"
