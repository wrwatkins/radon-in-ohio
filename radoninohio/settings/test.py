import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")  # nosec B105
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from .base import *  # noqa: E402,F401,F403

SECRET_KEY = "test-secret-key-not-for-production"  # nosec B105

DEBUG = False

ALLOWED_HOSTS = ["testserver", "localhost"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

STRIPE_SECRET_KEY = "sk_test_placeholder"  # nosec B105
STRIPE_WEBHOOK_SECRET = "whsec_test_placeholder"  # nosec B105
