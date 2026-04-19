from django.contrib import admin

from .models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    readonly_fields = ('created_at',)
