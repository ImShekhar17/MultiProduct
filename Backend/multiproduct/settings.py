"""
Django settings for MultiProduct project.

Supports:
- Environment-based configuration (.env)
- Celery/Redis integration
- JWT authentication (SimpleJWT)
- REST framework setup
- CORS and Email configuration
- i18n (Kannada, Tamil, English)
"""

import os
from pathlib import Path
from datetime import timedelta
from django.core.management.utils import get_random_secret_key
from django.utils.translation import gettext_lazy as _

# BASE CONFIGURATION

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env variables 
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass

# SECURITY SETTINGS

SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())
DEBUG = os.getenv("DEBUG", "True") in ("True", "true", "1")
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h
]

AUTH_USER_MODEL = os.getenv("AUTH_USER_MODEL", "authApp.User")

# INTERNATIONALIZATION
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("kn", _("Kannada")),
    ("ta", _("Tamil")),
]

# APPLICATIONS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    'social_django',

    # Third-party
    "django_celery_beat",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",

    # Local apps
    "authApp",
    "serviceApp",
]

# MIDDLEWARE

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "api.middleware.LanguageTranslationMiddleware",
    "multiproduct.middleware.LanguageTranslationMiddleware",
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',      # GOOGLE
    'social_core.backends.facebook.FacebookOAuth2',  # FACEBOOK
    'django.contrib.auth.backends.ModelBackend',
)


SOCIAL_AUTH_JSONFIELD_ENABLED = True

# GOOGLE OAUTH SETTINGS
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

# FACEBOOK SETTINGS
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "YOUR_FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "YOUR_FACEBOOK_APP_SECRET")

SOCIAL_AUTH_FACEBOOK_KEY = FACEBOOK_APP_ID
SOCIAL_AUTH_FACEBOOK_SECRET = FACEBOOK_APP_SECRET
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email'
}


# URLS / WSGI

ROOT_URLCONF = "multiproduct.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "multiproduct.wsgi.application"

# DATABASE CONFIGURATION
# DATABASES = {
#     "default": {
#         "ENGINE":"django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3"
#     }
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'Products'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'Samsung@5310'),
        'HOST': os.getenv('DB_HOST', 'db'), 
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# CACHE (Redis optional)

REDIS_URL = os.getenv("REDIS_URL", "")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }

# STATIC & MEDIA FILES

STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", BASE_DIR / "staticfiles")

MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", BASE_DIR / "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CELERY CONFIGURATION
from celery.schedules import crontab

import os

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# HYPER-SCALE OPTIMIZATIONS (1,000,000+ requests)
CELERY_BROKER_POOL_LIMIT = int(os.getenv("CELERY_POOL_LIMIT", 100)) # Minimize connection overhead
CELERY_TASK_ACKS_LATE = True # Ensure reliability at scale
CELERY_WORKER_PREFETCH_MULTIPLIER = int(os.getenv("CELERY_PREFETCH", 4)) # Optimized for fast tasks
CELERY_WORKER_CONCURRENCY = int(os.getenv("CELERY_CONCURRENCY", 8)) # Based on CPU/IO

# TASK ROUTING (Isolation for zero-latency)
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'high_priority': {
        'exchange': 'high_priority',
        'routing_key': 'high_priority',
    },
}

#cronjobs for notification
CELERY_BEAT_SCHEDULE = {
    "update": {
        "task": "authApp.scheduler.notification.send_notification",
        "schedule": timedelta(hours=5),
        "args": (12,),
    },
    "cleanup_otps": {
        "task": "authApp.tasks.send_mail_otp.cleanup_expired_otps",
        "schedule": crontab(minute=0, hour='*'),  # Run every hour
    },
}


# EMAIL CONFIGURATION

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "naurangilal9675329115@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "utik zhfb ryrh ucov")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# DJANGO REST FRAMEWORK CONFIG

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("API_PAGE_SIZE", 10)),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("DRF_THROTTLE_ANON", "100/day"),
        "user": os.getenv("DRF_THROTTLE_USER", "1000/day"),
        "username_check": os.getenv("DRF_THROTTLE_USERNAME_CHECK", "100/minute"),
    },
}

# SIMPLE JWT CONFIG

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", 60))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", 1))),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("JWT_SIGNING_KEY", SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# CORS CONFIGURATION

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True") in ("True", "true", "1")
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")

CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True") in ("True", "true", "1")
CORS_ALLOW_HEADERS = list(
    os.getenv("CORS_ALLOW_HEADERS", "content-type,authorization,x-csrftoken").split(",")
)

# LOGGING CONFIGURATION

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(message)s"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

# FEATURE FLAGS

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "http://localhost:8000")
ENABLE_RAZORPAY = os.getenv("ENABLE_RAZORPAY", "False") in ("True", "true", "1")

# END OF SETTINGS
