import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import QueryLog
from .serializers import QueryLogSerializer

logger = logging.getLogger(__name__)


class QueryCreateView(generics.CreateAPIView):
    """
    POST /api/query/  → Accept a query, store it in QueryLog, and return the saved entry.
    """
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Associate the query with the current authenticated user."""
        serializer.save(user=self.request.user)
        logger.info(
            "User '%s' submitted query: %s",
            self.request.user.username,
            serializer.instance.query_text[:80],
        )


class QueryListView(generics.ListAPIView):
    """
    GET /api/queries/  → List the authenticated user's query history (paginated).
    """
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only queries belonging to the current user."""
        return QueryLog.objects.filter(user=self.request.user)
