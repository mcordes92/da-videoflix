"""API views for user authentication including registration, login, token refresh, and logout."""
import django_rq
from django_rq import enqueue

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status, views, permissions, response

from .serializers import RegistrationSerializer, ActivationResponseSerializer, LoginSerializer

from .services import send_welcome_email, active_account, create_jwt_tokens, set_auth_cookies, clear_auth_cookies, blacklist_refresh_token, create_access_token_from_refresh, set_access_token


class RegistrationView(views.APIView):
    """Handle user registration."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Create a new user account."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            queue = django_rq.get_queue('high', autocommit=True)
            queue.enqueue(send_welcome_email, instance.email, instance.usertokenmodel.token, instance.usertokenmodel.uidb64)

            return response.Response(
                {
                    "user": {
                        "id": instance.id,
                        "email": instance.email
                    },
                "token": instance.usertokenmodel.token
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

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        access_token, refresh_token = create_jwt_tokens(user)

        res = response.Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email
                }
            },
            status=status.HTTP_200_OK
        )

        set_auth_cookies(res, access_token, refresh_token)
        return res
    
class LogoutView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_cookie = getattr(settings, "AUTH_REFRESH_COOKIE_NAME", "refresh_token")
        refresh_token = request.COOKIES.get(refresh_cookie)

        if not refresh_token:
            return response.Response({"detail": "Refresh token missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            blacklist_refresh_token(refresh_token)
        except Exception:
            pass

        res = response.Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )

        clear_auth_cookies(res)
        return res
    
class TokenRefreshView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_cookie = getattr(settings, "AUTH_REFRESH_COOKIE_NAME", "refresh_token")
        refresh_token = request.COOKIES.get(refresh_cookie)

        if not refresh_token:
            return response.Response({"detail": "Refresh token missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_access = create_access_token_from_refresh(refresh_token)
        except Exception:
            return response.Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        
        res = response.Response(
            {
                "detail": "Token refreshed",
                "access": new_access
            },
            status=status.HTTP_200_OK
        )

        set_access_token(res, new_access)
        return res