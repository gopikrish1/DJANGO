import logging

from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class UserSession(models.Model):
    """
    Tracks JWT tokens issued to users upon login.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="The user this session belongs to"
    )
    token = models.TextField(help_text="JWT access token issued at login")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'

