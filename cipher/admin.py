from django.contrib import admin
from .models import Text, RequestHistory, UserProfile

admin.site.register(Text)
admin.site.register(RequestHistory)
admin.site.register(UserProfile)