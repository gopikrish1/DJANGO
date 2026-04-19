import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer

logger = logging.getLogger(__name__)


class DocumentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/documents/  → List all documents for the authenticated user (paginated).
    POST /api/documents/  → Upload a new document.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only documents belonging to the current user."""
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically associate the uploaded document with the current user."""
        serializer.save(user=self.request.user)
        logger.info(
            "User '%s' uploaded document: %s",
            self.request.user.username,
            serializer.instance.title,
        )


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/documents/{id}/  → Retrieve a specific document.
    DELETE /api/documents/{id}/  → Delete a specific document.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only documents belonging to the current user."""
        return Document.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """Log document deletion before removing."""
        logger.info(
            "User '%s' deleted document: %s (id=%s)",
            self.request.user.username,
            instance.title,
            instance.id,
        )
        instance.delete()
