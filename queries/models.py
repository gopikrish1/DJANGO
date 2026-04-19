import logging

from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class QueryLog(models.Model):
    """
    Stores a user's query and the optional response.
    """
    query_text = models.TextField(help_text="The user's query text")
    response = models.TextField(
        blank=True,
        null=True,
        help_text="Optional response to the query"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='query_logs',
        help_text="User who submitted the query"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Query Log'
        verbose_name_plural = 'Query Logs'

    def __str__(self):
        return f"Query by {self.user.username} at {self.created_at:%Y-%m-%d %H:%M}"
