from django.contrib import admin
from gym_management.models import Subscription, Event, IndividualEvent, Tag

from users.models import User, PhoneNumberVerifySMS, Schedule

class CustomAdminSite(admin.AdminSite):
    site_header = "Администрирование ПАПА ФИТНЕС"
    side_title = "Панель управления ПАПА ФИТНЕС"
    index_title = "Добро пожаловать в админ-панель ПАПА ФИТНЕС"
    site_url = "https://red-store.site/admin"

custom_admin_site = CustomAdminSite(name="custom_admin")


class UserCustomAdmin(admin.ModelAdmin):
    fields = ("first_name", "last_name", "patronymic", "phone_number", "email", "description", "photo", "role", "rating", "trainer_type", "balance", "times", "date_joined", "last_login", "is_verified_email", "is_superuser")
    list_display = ("first_name", "last_name", "patronymic", "phone_number", "email", "role", "balance")
    filter_horizontal = ["times",]
    ordering = ("role",)


class ScheduleCustomAdmin(admin.ModelAdmin):
    list_display = ("time",)
    ordering = ("time",)


class PhoneNumberVerifySMSCustomAdmin(admin.ModelAdmin):
    list_display = ("code", "phone_number", "created", "expiration")
    ordering = ("created",)


class SubscriptionCustomAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "duration", "start_date", "price")
    ordering = ("user",)


class EventCustomAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "duration", "status", "start_date")
    filter_horizontal = ["participants", "tags"]
    ordering = ("start_date",)


class IndividualEventCustomAdmin(admin.ModelAdmin):
    list_display = ("coach", "participant", "quantity", "duration", "price",)
    ordering = ("training_date",)


class TagCustomAdmin(admin.ModelAdmin):
    fields = ("name",)
    list_display = ("name",)


custom_admin_site.register(User, UserCustomAdmin)
custom_admin_site.register(Subscription, SubscriptionCustomAdmin)
custom_admin_site.register(Event, EventCustomAdmin)
custom_admin_site.register(IndividualEvent, IndividualEventCustomAdmin)
custom_admin_site.register(Tag, TagCustomAdmin)
custom_admin_site.register(Schedule, ScheduleCustomAdmin)
custom_admin_site.register(PhoneNumberVerifySMS, PhoneNumberVerifySMSCustomAdmin)