from django.contrib import admin

from .models import Club, Event, IndividualEvent, Tag, Subscription

admin.site.register(Tag)
admin.site.register(IndividualEvent)
admin.site.register(Subscription)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "duration")
    ordering = ("title",)
    filter_horizontal = ["participants", "tags"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("address",)
    filter_horizontal = ["coaches"]
