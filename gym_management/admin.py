from django.contrib import admin

from .models import Club, Event, IndividualEvent, Subscription, Tag

admin.site.register(Tag)


@admin.register(IndividualEvent)
class IndividualEventAdmin(admin.ModelAdmin):
    list_display = ("coach", "participant")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("number", "user")
    readonly_fields = ("start_date", "end_date")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "duration")
    ordering = ("title",)
    filter_horizontal = ["participants", "tags"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("address",)
    filter_horizontal = ["coaches"]
