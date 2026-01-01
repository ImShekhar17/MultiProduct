import os
from dotenv import load_dotenv

load_dotenv()

# Django Core Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-to-a-secure-random-value')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
DJANGO_ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

AUTH_USER_MODEL = os.getenv('AUTH_USER_MODEL', 'authApp.User')

# Database
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
DB_NAME = os.getenv('DB_NAME', 'product')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'NauPos@234')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')

# Redis / Celery
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# Django Superuser
DJANGO_SUPERUSER_USERNAME = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
DJANGO_SUPERUSER_EMAIL = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
DJANGO_SUPERUSER_PASSWORD = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'naurangilal9675329115@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'utik zhfb ryrh ucov')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Product <naurangilal9675329115@gmail.com>')

# REST / JWT / CORS
JWT_ACCESS_MINUTES = int(os.getenv('JWT_ACCESS_MINUTES', '60'))
JWT_REFRESH_DAYS = int(os.getenv('JWT_REFRESH_DAYS', '1'))
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'
API_PAGE_SIZE = int(os.getenv('API_PAGE_SIZE', '10'))

# Other Config
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Kolkata')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENABLE_RAZORPAY = os.getenv('ENABLE_RAZORPAY', 'False') == 'True'
SITE_BASE_URL = os.getenv('SITE_BASE_URL', 'http://localhost:8000')

# Social Login
GOOGLE_CLIENT_ID = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', 'GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', 'GOOGLE_CLIENT_SECRET')

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', 'FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', 'FACEBOOK_APP_SECRET')
