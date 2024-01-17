from django.contrib import admin
from .models import Event, Tag

admin.site.register(Tag)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "duration")
    ordering = ("title",)
    filter_horizontal = ["participants", "tags"]