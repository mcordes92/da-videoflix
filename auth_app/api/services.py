from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from urllib.parse import urlencode

from rest_framework_simplejwt.tokens import RefreshToken

from ..models import UserTokenModel


def send_welcome_email(to_email: str, token: str, uidb64: str) -> None:
    subject = "Confirm your email"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)

    if not token:
        raise ValueError("token fehlt/leer")
    if not uidb64:
        raise ValueError("uidb64 fehlt/leer")

    base_url = getattr(settings, "FRONTEND_ACTIVATE_URL", None) or "http://localhost:5500/pages/auth/activate.html"
    query = urlencode({"uid": uidb64, "token": token})
    verify_url = f"{base_url}?{query}"

    html = render_to_string(
        "verify_email.html",
        {
            "subject": subject,
            "preheader": "Please verify your email address to activate your account.",
            "app_name": getattr(settings, "APP_NAME", None) or "Videoflix",
            "logo_url": getattr(settings, "EMAIL_LOGO_URL", None),
            "verify_url": verify_url,
            "year": getattr(settings, "EMAIL_YEAR", None),
        },
    )

    text = strip_tags(html)

    send_mail(
        subject=subject,
        message=text,
        from_email=from_email,
        recipient_list=[to_email],
        html_message=html,
        fail_silently=False,
    )


def active_account(uidb64, token: str) -> str:
    if not uidb64 or not token:
        raise ValueError("uidb64 or token is missing.")
    
    try:
        user_data = UserTokenModel.objects.select_related('user').get(uidb64=uidb64, token=token)
    except UserTokenModel.DoesNotExist:
        raise ValueError("Invalid uidb64 or token.")
    
    user =  user_data.user

    if user.is_active:
        return "Account is already activated."
    
    if user_data.token != token:
        raise ValueError("Invalid activation token.")
    
    user.is_active = True
    user.save(update_fields=['is_active'])

    UserTokenModel.delete(user_data)

    return "Account successfully activated."


def create_jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def set_auth_cookies(res, access_token: str, refresh_token: str):
    access_cookie = getattr(settings, "ACCESS_TOKEN_COOKIE_NAME", "access_token")
    refresh_cookie = getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token")

    secure = bool(getattr(settings, "AUTH_COOKIE_SECURE", False))
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")

    access_max_age = int(getattr(settings, "AUTH_ACCESS_COOKIE_MAX_AGE", 60 * 15))
    refresh_max_age = int(getattr(settings, "AUTH_REFRESH_COOKIE_MAX_AGE", 60 * 60 * 24 * 7))

    res.set_cookie(
        access_cookie,
        access_token,
        max_age=access_max_age,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/"
    )

    res.set_cookie(
        refresh_cookie,
        refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/"
    )

    return res


def clear_auth_cookies(res):
    access_cookie = getattr(settings, "ACCESS_TOKEN_COOKIE_NAME", "access_token")
    refresh_cookie = getattr(settings, "REFRESH_TOKEN_COOKIE_NAME", "refresh_token")

    secure = bool(getattr(settings, "AUTH_COOKIE_SECURE", False))
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")

    res.delete_cookie(
        access_cookie,
        path="/",
        samesite=samesite
    )

    res.delete_cookie(
        refresh_cookie,
        path="/",
        samesite=samesite
    )

    return res


def blacklist_refresh_token(refresh_token: str):
    token = RefreshToken(refresh_token)
    token.blacklist()


def create_access_token_from_refresh(refresh_token: str):
    token = RefreshToken(refresh_token)
    return str(token.access_token)


def set_access_token(res, access_token: str):
    access_cookie = getattr(settings, "ACCESS_TOKEN_COOKIE_NAME", "access_token")

    secure = bool(getattr(settings, "AUTH_COOKIE_SECURE", False))
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")

    access_max_age = int(getattr(settings, "AUTH_ACCESS_COOKIE_MAX_AGE", 60 * 15))

    res.set_cookie(
        access_cookie,
        access_token,
        max_age=access_max_age,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/"
    )

    return res