import os

from .settings import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")

SECURE_SSL_REDIRECT = True                 # send http:// to https://
SESSION_COOKIE_SECURE = True               # cookies only over https
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000             # tell browsers: https only, for a year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

MAILERS = {                                # Django 6.1: the console backend is rejected in production
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {"host": os.environ.get("SMTP_HOST", "smtp.example.com"), "port": 587, "use_tls": True},
    },
}
