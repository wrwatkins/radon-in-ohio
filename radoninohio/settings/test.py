import os
import sys

if not any("pytest" in arg for arg in sys.argv):
    raise RuntimeError(
        "radoninohio.settings.test is only intended for pytest. "
        "Never use it as the runtime DJANGO_SETTINGS_MODULE."
    )

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")  # nosec B105
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from .base import *  # noqa: E402,F401,F403

SECRET_KEY = "test-secret-key-not-for-production"  # nosec B105

DEBUG = False

ALLOWED_HOSTS = ["testserver", "localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

STRIPE_SECRET_KEY = "sk_test_placeholder"  # nosec B105
STRIPE_WEBHOOK_SECRET = "whsec_test_placeholder"  # nosec B105
