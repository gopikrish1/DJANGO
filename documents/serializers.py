from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Document model.
    The 'user' field is read-only and set automatically from the request.
    """

    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at', 'user']
        read_only_fields = ['id', 'uploaded_at', 'user']
