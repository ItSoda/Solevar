from django.contrib import admin

from .models import PhoneNumberVerifySMS, User

admin.site.register(User)
admin.site.register(PhoneNumberVerifySMS)
