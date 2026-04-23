import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import DocumentSerializer, IngestDocSerializer
from queries.ai_service import ingest_document

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


class DocumentDetailView(generics.RetrieveAPIView):
    """
    GET /api/documents/{id}/  → Retrieve a specific document.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only documents belonging to the current user."""
        return Document.objects.filter(user=self.request.user)


class IngestDocView(generics.GenericAPIView):
    """
    POST /api/documents/ingest-doc/
    Ingest a document into the FAISS vector store.
    Reads the file, chunks it, embeds the chunks, and stores them.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = IngestDocSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document_id = serializer.validated_data['document_id']

        # Validate that the document exists and belongs to the user
        try:
            document = Document.objects.get(
                id=document_id, user=request.user
            )
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get the actual file path on disk
        file_path = document.file.path

        try:
            chunks_created = ingest_document(file_path, document_id)
        except Exception as exc:
            logger.error("Ingestion failed for document %s: %s", document_id, exc)
            return Response(
                {"error": f"Failed to ingest document: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info(
            "User '%s' ingested document '%s' (%d chunks)",
            request.user.username,
            document.title,
            chunks_created,
        )

        return Response({
            "document_id": document_id,
            "title": document.title,
            "chunks_created": chunks_created,
            "status": "success",
        }, status=status.HTTP_200_OK)
