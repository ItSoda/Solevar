from django.db import models
from django.db.models import Max

from users.models import User


class Message(models.Model):
    """Model for message"""

    text = models.TextField()
    sent_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.sent_by}"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "Сообщения"


class Room(models.Model):
    """Model for room"""

    WAITING = "waiting"
    ACTIVE = "active"

    CHOICES_STATUS = (
        (WAITING, "Waiting"),
        (ACTIVE, "Active"),
    )

    uuid = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    messages = models.ManyToManyField(Message, blank=True)
    status = models.CharField(max_length=20, choices=CHOICES_STATUS, default=WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "чат"
        verbose_name_plural = "Чаты"

    def __str__(self):
        return f"{self.client} - {self.uuid}"

    def get_last_message(self):
        return self.messages.aggregate(last_message_time=Max("created_at"))[
            "last_message_time"
        ]
