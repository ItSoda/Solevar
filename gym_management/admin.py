from django.contrib import admin
from .models import Event, Tag, Club, IndividualEvent

admin.site.register(Tag)
admin.site.register(IndividualEvent)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "duration")
    ordering = ("title",)
    filter_horizontal = ["participants", "tags"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("address",)
    filter_horizontal = ["coaches"]