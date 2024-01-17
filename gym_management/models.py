from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=64)
    
    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f"Тег: {self.name}"


class Event(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()
    participants = models.ManyToManyField(User, related_name="participants_event")
    limit_of_participants = models.SmallIntegerField()
    tags = models.ManyToManyField(Tag)
    start_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "тренировку"
        verbose_name_plural = "Тренировки"

    def __str__(self):
        return f"Тренировка: {self.title} | {self.created_by}"