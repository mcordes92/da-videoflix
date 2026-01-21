"""API views for user authentication including registration, login, token refresh, and logout."""
import django_rq
from django_rq import enqueue

from django.contrib.auth.models import User
from rest_framework import status, views, permissions, response

from .serializers import RegistrationSerializer

from .services import send_welcome_email


class RegistrationView(views.APIView):
    """Handle user registration."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Create a new user account."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            queue = django_rq.get_queue('high', autocommit=True)
            queue.enqueue(send_welcome_email, instance.email, instance.userdatamodel.token, instance.userdatamodel.uidb64)

            return response.Response(
                {
                    "user": {
                        "id": instance.id,
                        "email": instance.email
                    },
                "token": instance.userdatamodel.token
                }, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
