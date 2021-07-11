"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path
from typing import Dict, Union  # isort:skip


def gettext(s):
    return s


DATA_DIR = os.path.dirname(os.path.dirname(__file__))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "2y(w)7nn$_05j$hm8hc%*7tf*%m-)ibqc)vh4=wo=g@nh5e^a8"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [os.getenv("DJANGO_ALLOWED_HOSTS", "*")]

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


STATIC_URL = "/static/"
MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(DATA_DIR, "media")
STATIC_ROOT = os.path.join(DATA_DIR, "static")
 
STATICFILES_DIRS = (os.path.join(BASE_DIR, "staticfiles"),)
SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.template.context_processors.csrf",
                "django.template.context_processors.tz",
                "sekizai.context_processors.sekizai",
                "django.template.context_processors.static",
                "cms.context_processors.cms_settings",
                "config.context_processors.get_global_context",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]


MIDDLEWARE = [
    "config.middleware.exception_middleware.ExceptionMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "djangocms_redirect.middleware.RedirectMiddleware",
]

CMS_APPS = [
    "djangocms_admin_style",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "cms",
    "menus",
    "sekizai",
    "treebeard",
    "djangocms_text_ckeditor",
    "filer",
    "easy_thumbnails",
    "ckeditor",
    "ckeditor_uploader",
]


CUSTOM_PLUGIN_APPS = [
    "config",
    "djangocms_redirect",
    "ads_txt",
]


# Application definition
INSTALLED_APPS = CMS_APPS + CUSTOM_PLUGIN_APPS

LANGUAGES = (
    # Customize this
    ("en", gettext("en")),
)

CMS_LANGUAGES = {
    # Customize this
    1: [
        {
            "code": "en",
            "name": gettext("en"),
            "redirect_on_fallback": True,
            "public": True,
            "hide_untranslated": False,
        },
    ],
    "default": {
        "redirect_on_fallback": True,
        "public": True,
        "hide_untranslated": False,
    },
}

CMS_TEMPLATES = (
    # Customize this
    ("fullwidth.html", "Fullwidth"),
    ("sidebar_left.html", "Sidebar Left"),
    ("sidebar_right.html", "Sidebar Right"),
)

X_FRAME_OPTIONS = "SAMEORIGIN"

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES: Dict[str, Dict[str, Union[str, int]]] = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": "localhost",
        "NAME": "statxumt_ringtonefly",
        "USER": "statxumt_ringtonefly",
        "PASSWORD": "}4lu.1o};GJ7",
        "PORT": "3306",
        "CONN_MAX_AGE": 500,
        "ATOMIC_REQUESTS": True,
    }
}


THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

SUPER_USER = {
    "ADMIN_EMAIL": "admin@ringtonefly.com",
    "ADMIN_USERNAME":"ringtonefly",
    "ADMIN_PASSWORD": "password@123"
}


#########
#  CKEDITOR CONFIGURATION #
#########

CKEDITOR_JQUERY_URL = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js"

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    "default": {"toolbar": None},
}


DJANGOCMS_REDIRECT_USE_REQUEST = True
ADSTXT_CACHE_TIMEOUT = 60*60*24

PREPEND_WWW = True