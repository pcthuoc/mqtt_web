from django.contrib import admin
from .models import APIKey

class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'api_key', 'user')  # Add 'user' to display the associated user

admin.site.register(APIKey, APIKeyAdmin)