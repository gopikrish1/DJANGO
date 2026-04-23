import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import QueryLog
from .serializers import AskAISerializer, RAGQuerySerializer, QueryLogSerializer
from .ai_service import ask_ai, rag_query

logger = logging.getLogger(__name__)


class AskAIView(generics.GenericAPIView):
    """
    POST /api/ask-ai/
    Direct LLM Q&A with prompt templates.
    Logs the interaction to QueryLog with from_rag=False.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AskAISerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']

        try:
            answer = ask_ai(question)
        except Exception as exc:
            logger.error("AskAI failed: %s", exc)
            return Response(
                {"error": "Failed to generate AI response. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Log the query
        QueryLog.objects.create(
            query_text=question,
            response=answer,
            from_rag=False,
            user=request.user,
        )

        logger.info(
            "User '%s' asked AI: %s", request.user.username, question[:80]
        )

        return Response({
            "question": question,
            "answer": answer,
        }, status=status.HTTP_200_OK)


class RAGQueryView(generics.GenericAPIView):
    """
    POST /api/rag-query/
    RAG-based document query.
    Retrieves relevant chunks from FAISS, augments the prompt, and calls the LLM.
    Logs the interaction to QueryLog with from_rag=True.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RAGQuerySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']

        try:
            result = rag_query(question)
        except Exception as exc:
            logger.error("RAG query failed: %s", exc)
            return Response(
                {"error": "Failed to process RAG query. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Log the query
        QueryLog.objects.create(
            query_text=question,
            response=result["answer"],
            from_rag=True,
            user=request.user,
        )

        logger.info(
            "User '%s' RAG query: %s", request.user.username, question[:80]
        )

        return Response({
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
        }, status=status.HTTP_200_OK)


class QueryHistoryView(generics.ListAPIView):
    """
    GET /api/query-history/
    Paginated query history for the authenticated user.
    Supports filtering by from_rag query param: ?from_rag=true or ?from_rag=false
    """
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return queries belonging to the current user, with optional filtering."""
        qs = QueryLog.objects.filter(user=self.request.user)

        # Optional filter by from_rag
        from_rag_param = self.request.query_params.get('from_rag')
        if from_rag_param is not None:
            from_rag_value = from_rag_param.lower() in ('true', '1', 'yes')
            qs = qs.filter(from_rag=from_rag_value)

        return qs
