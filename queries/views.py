import logging
import os

from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from openai import OpenAI

from .models import QueryLog
from .serializers import QueryLogSerializer

logger = logging.getLogger(__name__)

# Initialize the OpenAI client. It automatically picks up OPENAI_API_KEY from environment variables.
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))


class QueryCreateView(generics.CreateAPIView):
    """
    POST /api/query/  → Accept a query, store it in QueryLog, and return the saved entry.
    """
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Associate the query with the current authenticated user and get OpenAI response."""
        query_text = serializer.validated_data.get('query_text', '')
        
        response_text = None
        try:
            # Call the OpenAI API
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo", # or "gpt-4o", depending on what your key supports
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query_text}
                ]
            )
            response_text = completion.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI API Error: %s", e)
            response_text = "Sorry, there was an error generating a response."

        # Save both the user and the generated response
        serializer.save(user=self.request.user, response=response_text)
        
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
