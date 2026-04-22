import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import UserSession

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    POST /api/auth/login/

    Accepts 'username' and 'password', authenticates the user,
    generates JWT tokens, stores the access token in UserSession,
    and returns both tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Validate input
        if not username or not password:
            return Response(
                {'error': 'Both username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate
        user = authenticate(username=username, password=password)
        if user is None:
            logger.warning("Failed login attempt for username: %s", username)
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Store the session
        UserSession.objects.create(user=user, token=access_token)
        logger.info("User '%s' logged in successfully.", username)

        return Response(
            {
                'username': user.username,
                'access': access_token,
                'refresh': str(refresh),
            },
            status=status.HTTP_200_OK,
        )
