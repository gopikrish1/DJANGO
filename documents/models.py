import logging

from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class Document(models.Model):
    """
    Represents an uploaded document associated with a user.
    """
    title = models.CharField(max_length=255, help_text="Title of the document")
    file = models.FileField(upload_to='documents/', help_text="Uploaded file")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Owner of the document"
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

