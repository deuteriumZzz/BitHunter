import os
from pathlib import Path

from cryptography.fernet import Fernet

# Base settings
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: Используем env с fallback (хорошо, но не забудь сменить в проде!)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "fallback-secret-key-change-in-prod")

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    FERNET_KEY = Fernet.generate_key().decode()
    # Рекомендация: сохранить в .env файл вручную после генерации

# DEBUG: По умолчанию False для безопасности, включай явно в dev
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# ALLOWED_HOSTS: Разделяем по запятым и убираем пробелы
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
]

# AWS: Добавил env для bucket name, и проверки на наличие ключей (чтобы избежать ошибок)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv(
    "AWS_S3_BUCKET_NAME", "bithunter-models"
)  # Теперь configurable

# Sentry: Хорошо, но добавь проверку на DSN
if os.getenv("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[DjangoIntegration()])

# INSTALLED_APPS: Определяем список сначала
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "channels",
    "celery",
    "accounts",
    "alerts",
    "analytics",
    "trading",
    "api",
    "news",  # Добавлено
]

# Prometheus: Теперь добавляем ПОСЛЕ определения INSTALLED_APPS
if "django_prometheus" not in INSTALLED_APPS:  # Проверка, чтобы не дублировать
    INSTALLED_APPS.append("django_prometheus")

# MIDDLEWARE: Определяем список сначала
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Стандартный Django middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Если используешь CORS
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.SecurityMiddleware",  # Теперь ссылка на импортированный класс (без дублирования!)
    # Добавь другие, если нужно, например, для JWT или кастомных
]

# Prometheus middleware: Добавляем ПОСЛЕ определения MIDDLEWARE
if "django_prometheus.middleware.PrometheusBeforeMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(0, "django_prometheus.middleware.PrometheusBeforeMiddleware")
    MIDDLEWARE.append("django_prometheus.middleware.PrometheusAfterMiddleware")

# Остальные настройки без изменений (или с небольшими улучшениями)
ROOT_URLCONF = "bithunter.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "bithunter.wsgi.application"
ASGI_APPLICATION = "bithunter.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "bithunter"),
        "USER": os.environ.get("DB_USER", "user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "100/hour",  # Ограничение для API новостей
    },
}

# Channels: Сделал хосты configurable через env
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (
                    os.getenv("REDIS_HOST", "127.0.0.1"),
                    int(os.getenv("REDIS_PORT", 6379)),
                )
            ],
        },
    },
}

# Celery: Аналогично, configurable
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")

# Cache: Configurable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("CACHE_LOCATION", "redis://127.0.0.1:6379/1"),
    }
}

# Logging: Расширил для лучших практик (добавил уровни и обработку)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(
                BASE_DIR, "logs", "django.log"
            ),  # Добавь папку logs в проект
            "formatter": "verbose",
        },
        "celery": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/celery.log",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["celery"],
            "level": "INFO",
        },
    },
}

# Дополнительная безопасность для продакшена
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Перенаправление на HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
