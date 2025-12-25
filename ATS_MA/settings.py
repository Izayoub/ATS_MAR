from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&o59@uc+e4+%e$16h4nl0agnw2&-=8feoekq8otq@!#djrixin'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',  # CORRECTION: Supprimé le 'ù' au début
    'django_extensions',
    'accounts',
    'recruitment',
    'ai_engine',  # désactivé
    'analytics',
    'corsheaders',
]

AI_ENGINE_SETTINGS = {
    # Service de matching
    'MATCHING': {
        'MODEL_NAME': 'BAAI/bge-m3',
        'CACHE_TIMEOUT': 3600,  # 1 heure
        'ENABLE_CACHE': True,
        'MAX_BATCH_SIZE': 100,
        'LOG_LEVEL': 'INFO',
        'PRELOAD_MODEL': True,  # Charger le modèle au démarrage
    },

    # Performance
    'PERFORMANCE': {
        'MAX_CONCURRENT_REQUESTS': 10,
        'REQUEST_TIMEOUT': 30,  # secondes
        'ENABLE_METRICS': True,
    },

    # Sécurité
    'SECURITY': {
        'RATE_LIMIT_PER_HOUR': 1000,
        'REQUIRE_AUTH': False,  # Pour API publique
        'ALLOWED_DOMAINS': ['*'],  # Ou spécifiez vos domaines
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ai-engine-cache',
    },
    'matching': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'matching_',
        'TIMEOUT': AI_ENGINE_SETTINGS['MATCHING']['CACHE_TIMEOUT'],
    }
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # doit être tout en haut
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# Permettre les cookies CSRF
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Headers autorisés
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Méthodes autorisées
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Permettre les cookies (si nécessaire)
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'ATS_MA.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ATS_MA.wsgi.application'

CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Ou votre broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Configuration PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ATS',
        'USER': 'ayoub',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configuration pour l'IA
AI_CONFIG = {
    'MISTRAL_MODEL_PATH': 'models/mistral-7b-quantized',
    'BGE_MODEL_PATH': 'models/bge-m3',
    'PADDLE_OCR_PATH': 'models/paddleocr',
    'SENTENCE_BERT_PATH': 'models/sentence-bert-multilingual',
    'VECTOR_DB_PATH': 'data/vector_store',
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_USER_MODEL = 'accounts.CustomUser'

# AJOUT: Configuration de l'URL de connexion
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'api/recruitment/joboffers/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('fr', 'Français'),
    ('ar', 'العربية'),
    ('en', 'English'),
]
TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Configuration pour les uploads de CV
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB

# Types de fichiers autorisés pour les CV
ALLOWED_CV_FORMATS = ['.pdf', '.txt', '.doc', '.docx']
MAX_CV_FILE_SIZE = 5 * 1024 * 1024  # 5MB

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'