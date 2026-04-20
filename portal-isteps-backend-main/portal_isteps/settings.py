"""
Django settings for portal_isteps project.
"""

from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Apps del Portal ISTEPS
    "auth_app",
    "integration",
    "analytics",
    "content",
    "system_app",
    "api",
    # Django REST Framework
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_yasg",
    # Django Allauth (Microsoft 365 login)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.microsoft",
    # OAuth Toolkit (Para ser provider)
    "oauth2_provider",
    # Protección brute force
    "axes",
]


# DJANGO SITES FRAMEWORK

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "axes.middleware.AxesMiddleware",
]


# AUTHENTICATION BACKENDS

AUTHENTICATION_BACKENDS = [
    # Django admin
    "django.contrib.auth.backends.ModelBackend",
    # Allauth (Microsoft 365)
    "allauth.account.auth_backends.AuthenticationBackend",
    # Axes (protección brute force)
    "axes.backends.AxesStandaloneBackend",
]

ROOT_URLCONF = "portal_isteps.urls"

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

WSGI_APPLICATION = "portal_isteps.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Primero intentar usar DATABASE_URL (Railway/Producción)
DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    # Configuración para Railway (usando DATABASE_URL)
    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # Configuración para desarrollo local (usando variables individuales)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }


# CUSTOM USER MODEL

AUTH_USER_MODEL = "auth_app.Usuario"


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "es-ec"

TIME_ZONE = "America/Guayaquil"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# DJANGO REST FRAMEWORK CONFIGURATION


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M:%S",
}


# JWT CONFIGURATION

SIMPLE_JWT = {
    # Duración de los tokens
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Permitir renovar refresh tokens
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    # Algoritmo de encriptación
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    # Claims del token
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}


# CORS CONFIGURATION


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


# DJANGO ALLAUTH CONFIGURATION


# DJANGO ALLAUTH CONFIGURATION


# Configuración general de allauth
ACCOUNT_EMAIL_VERIFICATION = "none"  # Microsoft 365 ya verifica emails

# DESHABILITAR registro/login tradicional - SOLO Microsoft 365
ACCOUNT_ALLOW_REGISTRATION = False  # ← Deshabilita signup tradicional
ACCOUNT_LOGIN_ON_GET = False  # Previene auto-login en GET requests

# Redirigir al endpoint que devuelve JWT después del login
LOGIN_REDIRECT_URL = "/api/auth/social-token/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Solo permitir login social (Microsoft 365)
SOCIALACCOUNT_ONLY = True  # ← Fuerza uso de social auth únicamente
SOCIALACCOUNT_AUTO_SIGNUP = True  # Auto-crear usuarios desde Microsoft

# Configuración de Microsoft 365
SOCIALACCOUNT_PROVIDERS = {
    "microsoft": {
        "TENANT": config("MICROSOFT_TENANT_ID"),
        "SCOPE": [
            "User.Read",
            "email",
            "profile",
            "openid",
        ],
    }
}


# DJANGO OAUTH TOOLKIT CONFIGURATION


OAUTH2_PROVIDER = {
    "SCOPES": {
        "read": "Read scope",
        "write": "Write scope",
        "groups": "Access to your groups",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": 7200,  # 2 horas
    "REFRESH_TOKEN_EXPIRE_SECONDS": 604800,  # 7 días
}


# DJANGO AXES CONFIGURATION (Brute Force Protection)


AXES_FAILURE_LIMIT = 5  # Bloquear después de 5 intentos fallidos
AXES_COOLOFF_TIME = 1  # 1 hora de bloqueo
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]


# OAUTH2 PROVIDER CONFIGURATION
OAUTH2_PROVIDER = {
    # Duración de los tokens de acceso (1 hora)
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,
    # Duración de los tokens de autorización (10 minutos)
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 600,
    # Duración de los refresh tokens (14 días)
    "REFRESH_TOKEN_EXPIRE_SECONDS": 1209600,
    # Permitir que aplicaciones usen el mismo token múltiples veces
    "ROTATE_REFRESH_TOKEN": False,
    # Scopes disponibles
    "SCOPES": {
        "read": "Acceso de lectura",
        "write": "Acceso de escritura",
        "profile": "Acceso al perfil del usuario",
        "email": "Acceso al email del usuario",
    },
    # Scope por defecto
    "DEFAULT_SCOPES": ["read", "profile", "email"],
    # Modelo de usuario personalizado
    "OAUTH2_BACKEND_CLASS": "oauth2_provider.oauth2_backends.JSONOAuthLibCore",
}


# CONFIGURACIÓN PARA PRODUCCIÓN (Railway)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
# CONFIGURACIÓN DE ARCHIVOS MEDIA (Imágenes, PDFs subidos)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Permitir host de Railway
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
