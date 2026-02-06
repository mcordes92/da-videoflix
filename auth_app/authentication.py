from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads the access token from cookies
    instead of the Authorization header.
    """
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        
        if access_token is None:
            return None
        
        try:
            validated_token = self.get_validated_token(access_token)
        except (InvalidToken, TokenError):
            return None
        
        return self.get_user(validated_token), validated_token