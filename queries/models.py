import logging

from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class QueryLog(models.Model):
    """
    Stores a user's query and the optional response.
    The `from_rag` flag indicates whether the response was generated
    using the RAG pipeline (True) or direct LLM call (False).
    """
    query_text = models.TextField(help_text="The user's query text")
    response = models.TextField(
        blank=True,
        null=True,
        help_text="Optional response to the query"
    )
    from_rag = models.BooleanField(
        default=False,
        help_text="True if response was generated via RAG pipeline"
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
        label = "RAG" if self.from_rag else "AI"
        return f"[{label}] {self.query_text[:50]}"
