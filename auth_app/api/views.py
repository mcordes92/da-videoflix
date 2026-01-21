"""API views for user authentication including registration, login, token refresh, and logout."""
import django_rq
from django_rq import enqueue

from django.contrib.auth.models import User
from rest_framework import status, views, permissions, response

from .serializers import RegistrationSerializer, ActivationResponseSerializer

from .services import send_welcome_email, active_account


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
    
class ActivationView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            msg = active_account(uidb64=uidb64, token=token)
            data = {"message": msg}
            return response.Response(data, status=status.HTTP_200_OK)
        except Exception:
            return response.Response({"message": "Activation failed."}, status=status.HTTP_400_BAD_REQUEST)
