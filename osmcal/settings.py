import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("OSMCAL_SECRET", "03#2of3$kqqxc&=rz#qkm^+2cl)0al@0k@2c)qx-$rq34m&q55")
DEBUG = os.getenv("OSMCAL_PROD", False) not in ["True", "true", "yes", "1"]

ENABLE_COMMUNITIES = False

if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]

ALLOWED_HOSTS = [os.getenv("OSMCAL_HOST", "*")]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "leaflet",
    "background_task",
    "osmcal",
    "osmcal.api",
    "osmcal.community",
    "osmcal.social",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "osmcal.middlewares.replay_middleware.ReplayMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not DEBUG:
    prometheus_dir = os.getenv("prometheus_multiproc_dir", "/tmp/osmcal")
    if not os.path.exists(prometheus_dir):
        os.makedirs(prometheus_dir, exist_ok=True)

    INSTALLED_APPS.append("django_prometheus")
    MIDDLEWARE.insert(0, "django_prometheus.middleware.PrometheusBeforeMiddleware")
    MIDDLEWARE.append("django_prometheus.middleware.PrometheusAfterMiddleware")

ROOT_URLCONF = "osmcal.urls"

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

WSGI_APPLICATION = "osmcal.wsgi.application"

WRITABLE_REGION: Optional[str] = os.getenv("WRITABLE_REGION", None)
CURRENT_REGION: Optional[str] = os.getenv("FLY_REGION", None)

DATABASES = {
    "default": {
        "HOST": os.getenv("OSMCAL_PG_HOST", ""),
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("OSMCAL_PG_DB", "osmcal"),
        "USER": os.getenv("OSMCAL_PG_USER", "osmcal"),
        "PASSWORD": os.getenv("OSMCAL_PG_PASSWORD", None),
        "PORT": 5432 if WRITABLE_REGION == CURRENT_REGION else 5433,
    }
}

CONN_MAX_AGE = 3600

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

OAUTH_OPENSTREETMAP_KEY = os.getenv("OSMCAL_OSM_KEY", "")
OAUTH_OPENSTREETMAP_SECRET = os.getenv("OSMCAL_OSM_SECRET", "")

OAUTH2_OPENSTREETMAP_CLIENT_ID = os.getenv("OSMCAL_OAUTH2_CLIENT_ID", "")
OAUTH2_OPENSTREETMAP_CLIENT_SECRET = os.getenv("OSMCAL_OAUTH2_CLIENT_SECRET", "")

AUTH_USER_MODEL = "osmcal.User"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGIN_URL = "/login/"

if not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.getenv("OSMCAL_SENTRY_URL"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.01,
    )

LEAFLET_CONFIG = {"RESET_VIEW": False, "MAX_ZOOM": 19, "ATTRIBUTION_PREFIX": False}

SOCIAL = {
    "mastodon": {"access_token": os.getenv("MASTODON_ACCESS_TOKEN", None)},
}

if gdal_path := os.getenv("GDAL_LIBRARY_PATH", None):
    GDAL_LIBRARY_PATH = gdal_path

if geos_path := os.getenv("GEOS_LIBRARY_PATH", None):
    GEOS_LIBRARY_PATH = geos_path
