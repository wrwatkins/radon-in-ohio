from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # nosec B104 — hostname list, not a bind address

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
