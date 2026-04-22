from rest_framework import serializers

from .models import QueryLog


class QueryLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the QueryLog model.
    'response' is optional on input; 'user' and 'created_at' are read-only.
    """

    class Meta:
        model = QueryLog
        fields = ['id', 'query_text', 'response', 'created_at', 'user']
        read_only_fields = ['id', 'response', 'created_at', 'user']
