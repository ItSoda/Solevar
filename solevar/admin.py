from django.contrib import admin

from chats.models import Message, Room
from gym_management.models import Event, IndividualEvent, Subscription, Tag
from tgbot.models import Admin, News
from users.models import AudioRecord, PhoneNumberVerifySMS, Schedule, User


class CustomAdminSite(admin.AdminSite):
    site_header = "Администрирование ПАПА ФИТНЕС"
    side_title = "Панель управления ПАПА ФИТНЕС"
    index_title = "Добро пожаловать в панель администратора ПАПА ФИТНЕС"
    site_url = "https://red-store.site/admin"


custom_admin_site = CustomAdminSite(name="admin_panel")


class UserCustomAdmin(admin.ModelAdmin):
    fields = (
        "first_name",
        "last_name",
        "patronymic",
        "date_of_birth",
        "phone_number",
        "email",
        "description",
        "photo",
        "photo_file",
        "role",
        "rating",
        "trainer_type",
        "balance",
        "date_joined",
        "last_login",
        "is_verified_email",
        "is_superuser",
        "passport_series",
        "passport_number",
        "date_of_issue",
        "place_of_issue",
        "registration_address",
        "records_files",
    )
    list_display = (
        "first_name",
        "last_name",
        "patronymic",
        "phone_number",
        "email",
        "role",
        "balance",
    )
    ordering = ("role",)
    filter_horizontal = ("records_files",)


class ScheduleCustomAdmin(admin.ModelAdmin):
    list_display = ("time", "is_selected")
    ordering = ("time", "coach")
    filter_horizontal = ("coach",)


class RoomCustomAdmin(admin.ModelAdmin):
    list_display = ("client", "status")
    filter_horizontal = ("messages",)


class AdminCustomAdmin(admin.ModelAdmin):
    list_display = ("UUID",)


class NewsCustomAdmin(admin.ModelAdmin):
    list_display = ("title",)


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
    list_display = (
        "coach",
        "participant",
        "quantity",
        "duration",
        "price",
    )
    ordering = ("training_date",)


class TagCustomAdmin(admin.ModelAdmin):
    fields = ("name",)
    list_display = ("name",)


custom_admin_site.register(AudioRecord)
custom_admin_site.register(Message)
custom_admin_site.register(Room, RoomCustomAdmin)
custom_admin_site.register(Admin, AdminCustomAdmin)
custom_admin_site.register(News, NewsCustomAdmin)
custom_admin_site.register(User, UserCustomAdmin)
custom_admin_site.register(Subscription, SubscriptionCustomAdmin)
custom_admin_site.register(Event, EventCustomAdmin)
custom_admin_site.register(IndividualEvent, IndividualEventCustomAdmin)
custom_admin_site.register(Tag, TagCustomAdmin)
custom_admin_site.register(Schedule, ScheduleCustomAdmin)
custom_admin_site.register(PhoneNumberVerifySMS, PhoneNumberVerifySMSCustomAdmin)
