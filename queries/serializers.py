from rest_framework import serializers

from .models import QueryLog


class AskAISerializer(serializers.Serializer):
    """Input serializer for POST /api/ask-ai/"""
    question = serializers.CharField(
        help_text="The question to ask the AI"
    )


class RAGQuerySerializer(serializers.Serializer):
    """Input serializer for POST /api/rag-query/"""
    question = serializers.CharField(
        help_text="The question to ask against ingested documents"
    )


class QueryLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the QueryLog model.
    Used for query history responses.
    """

    class Meta:
        model = QueryLog
        fields = ['id', 'query_text', 'response', 'from_rag', 'created_at', 'user']
        read_only_fields = ['id', 'query_text', 'response', 'from_rag', 'created_at', 'user']
