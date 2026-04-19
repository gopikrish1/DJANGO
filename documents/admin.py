from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('title',)
    readonly_fields = ('uploaded_at',)
