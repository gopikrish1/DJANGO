from rest_framework import serializers

from .models import UserSession


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserSession model.
    All fields are read-only — sessions are created internally on login.
    """

    class Meta:
        model = UserSession
        fields = ['id', 'user', 'token', 'created_at']
        read_only_fields = ['id', 'user', 'token', 'created_at']
