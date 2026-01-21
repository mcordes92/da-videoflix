from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from urllib.parse import urlencode


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
