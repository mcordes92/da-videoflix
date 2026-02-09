import secrets, django_rq
from django_rq import enqueue

from django.conf import settings
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken

from ..models import UserTokenModel
from .tasks import send_password_reset_email

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
    access_cookie = getattr(settings, "AUTH_ACCESS_COOKIE_NAME", "access_token")
    refresh_cookie = getattr(settings, "AUTH_REFRESH_COOKIE_NAME", "refresh_token")

    secure = bool(getattr(settings, "AUTH_COOKIE_SECURE", False))
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "AUTH_COOKIE_DOMAIN", None)

    access_max_age = int(getattr(settings, "AUTH_ACCESS_COOKIE_MAX_AGE", 60 * 15))
    refresh_max_age = int(getattr(settings, "AUTH_REFRESH_COOKIE_MAX_AGE", 60 * 60 * 24 * 7))

    cookie_kwargs = {
        "httponly": True,
        "secure": secure,
        "samesite": samesite,
        "path": "/"
    }
    
    if domain:
        cookie_kwargs["domain"] = domain

    res.set_cookie(
        access_cookie,
        access_token,
        max_age=access_max_age,
        **cookie_kwargs
    )

    res.set_cookie(
        refresh_cookie,
        refresh_token,
        max_age=refresh_max_age,
        **cookie_kwargs
    )

    return res


def clear_auth_cookies(res):
    access_cookie = getattr(settings, "AUTH_ACCESS_COOKIE_NAME", "access_token")
    refresh_cookie = getattr(settings, "AUTH_REFRESH_COOKIE_NAME", "refresh_token")
    
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "AUTH_COOKIE_DOMAIN", None)

    delete_kwargs = {
        "path": "/",
        "samesite": samesite
    }
    
    if domain:
        delete_kwargs["domain"] = domain

    res.delete_cookie(access_cookie, **delete_kwargs)
    res.delete_cookie(refresh_cookie, **delete_kwargs)

    return res


def blacklist_refresh_token(refresh_token: str):
    token = RefreshToken(refresh_token)
    token.blacklist()


def create_access_token_from_refresh(refresh_token: str):
    token = RefreshToken(refresh_token)
    return str(token.access_token)


def set_access_token(res, access_token: str):
    access_cookie = getattr(settings, "AUTH_ACCESS_COOKIE_NAME", "access_token")

    secure = bool(getattr(settings, "AUTH_COOKIE_SECURE", False))
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "AUTH_COOKIE_DOMAIN", None)

    access_max_age = int(getattr(settings, "AUTH_ACCESS_COOKIE_MAX_AGE", 60 * 15))

    cookie_kwargs = {
        "httponly": True,
        "secure": secure,
        "samesite": samesite,
        "path": "/"
    }
    
    if domain:
        cookie_kwargs["domain"] = domain

    res.set_cookie(
        access_cookie,
        access_token,
        max_age=access_max_age,
        **cookie_kwargs
    )

    return res


def create_password_reset(user: User):
    token = secrets.token_urlsafe(20)

    obj, _ = UserTokenModel.objects.get_or_create(user=user)
    obj.token = token
    obj.save()

    uidb64 = str(obj.uidb64)

    queue = django_rq.get_queue('high', autocommit=True)
    queue.enqueue(send_password_reset_email, user, obj.token, uidb64)

def confirm_password_reset(uidb64: str, token: str, new_password: str):
    try:
        user_data = UserTokenModel.objects.select_related("user").get(uidb64=uidb64, token=token)
    except UserTokenModel.DoesNotExist:
        raise ValueError("Invalid token or uidb64.")
    
    user = user_data.user
    user.set_password(new_password)
    user.save(update_fields=["password"])

    user_data.delete()