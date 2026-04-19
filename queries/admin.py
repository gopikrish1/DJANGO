from django.contrib import admin

from .models import QueryLog


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'query_text', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('query_text',)
    readonly_fields = ('created_at',)
