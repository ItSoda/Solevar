from django.contrib import admin

from .models import PhoneNumberVerifySMS, User, Schedule

admin.site.register(User)
admin.site.register(PhoneNumberVerifySMS)
admin.site.register(Schedule)