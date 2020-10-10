"""
Django settings for yas project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ

base = environ.Path(__file__) - 2
env = environ.Env()
environ.Env.read_env(env_file=base('.env'))
DEBUG = env.bool('DEBUG', default=False)
HTML_MINIFY = env.bool('HTML_MINIFY', default=False)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h8e4=j8i1(j$^_#rh735453!+9ygji@y3bevk@x58dajt5*v0n'

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'django_su',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
#    'debug_toolbar',
    'easy_thumbnails',
    'easy_thumbnails.optimize',
    'social_django',
    'crispy_forms',
    'import_export',
    'fullurl',
    'post_office',
    'tags_input',
    'froala_editor',
    'ckeditor',
    'ckeditor_uploader',
    'yas',
    'core',
    'search',
    'places',
    'reviews',
    'ads',
    'lodges',
    'analytics',
    'blog',
    'operators',
    'extras',
    'photos',
    'users',
    'backend',
    'cookielaw',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'operators.SetLastVisitMiddleware.SetLastVisitMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
]


DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False,}
SHOW_TOOLBAR_CALLBACK = True
ROOT_URLCONF = 'yas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.all_countries',
                'core.context_processors.footer_countries',
                'core.context_processors.footer_parks',
                'core.context_processors.footer_pages',
                'core.context_processors.footer_reviews',
                'core.context_processors.footer_blog',
                'core.context_processors.login_form',
                'core.context_processors.site_constants',
                'core.context_processors.favs_count',
                'django_su.context_processors.is_su',
            ],
        },
    },
]

# social auth backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.facebook.FacebookOAuth2',  # for Facebook authentication
    'social_core.backends.open_id.OpenIdAuth',  # for Google authentication
    'social_core.backends.google.GoogleOpenId',  # for Google authentication
    'social_core.backends.google.GoogleOAuth2',  # for Google authentication
    'users.UserEmailBackend.UserEmailBackend',
    'django_su.backends.SuBackend'
]

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',  # <--- enable this one
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email',
}
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True


# social auth keys for facebook authentication
SOCIAL_AUTH_FACEBOOK_KEY = env.str('FACEBOOK_KEY')        # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = env.str('FACEBOOK_SECRET')  # App Secret



# social auth keys for google authentication
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '521830571900-2gd8qs0uldik5r11nc02a5ffl8360rri.apps.googleusercontent.com'  # CLient Id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '31jgpPaJAje3hEkHnSaHGluR'  # Client Secret
USE_X_FORWARDED_HOST = True

#if not DEBUG:
#    SECURE_SSL_REDIRECT = True
#    CSRF_COOKIE_SECURE = True
#    SESSION_COOKIE_SECURE = True

LOGIN_REDIRECT_URL = 'home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'home'

WSGI_APPLICATION = 'yas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env.str('DB_ENGINE'),
        'HOST': env.str('DB_HOST'),
        'PORT': env.str('DB_PORT'),
        'NAME': env.str('DB_NAME'),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'node_modules'),
    os.path.join(BASE_DIR, 'bower_components'),
    os.path.join(BASE_DIR, 'photos'),
    os.path.join(BASE_DIR, 'backend'),
    os.path.join(BASE_DIR, 'operators'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

THUMBNAIL_ALIASES = {
    '': {
        'crop_50': {'size': (50, 50), 'crop': True},
        '4185x1395':{'size': (4185, 1395), 'crop': True},
        'crop_150': {'size': (150, 150), 'crop': True},
        'crop_200': {'size': (200, 200), 'crop': True},
        'crop_500x400': {'size': (500, 400), 'crop': True},
        'crop_250': {'size': (250, 250), 'crop': True},
        'crop_300': {'size': (300, 300), 'crop': True},
        'crop_300_150': {'size': (300, 150), 'crop': True},
        'crop_160_90':  {'size': (160, 90), 'crop': True},
        'card': {'size': (340, 255), 'crop': True},
        'search_card': {'size': (188, 108), 'crop': True},
        'crop_790_400': {'size': (790, 400), 'crop': True},
        '579x381': {'size': (579, 381), 'crop': True},
        '770x383': {'size': (770, 383), 'crop': True},
        '1441x577': {'size': (1441, 577), 'crop': True},
        '1920x640': {'size': (1920, 640), 'crop': True},
        '3851x1155': {'size': (3851, 1155), 'crop': True},
        'default': {},
    },
}



THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/usr/bin/optipng {filename}',
    'gif': '/usr/bin/optipng {filename}',
    'jpeg': '/usr/bin/jpegoptim {filename}'
}


PASSWORD_HASHERS = [
    'yas.hashers.SHA1PasswordHasher',
]

if not DEBUG:
    # importing logger settings
    try:
        from logger_settings import *
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn="https://c221035eefa14a37949b7ebcafaacd6e@o459524.ingest.sentry.io/5458806",
            integrations=[DjangoIntegration()],
            traces_sample_rate=1.0,

            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True
        )
    except Exception as e:
        # in case of any error, pass silently.
        pass


RECAPTCHA_SECRET_KEY = env.str('RECAPTCHA_SECRET_KEY')
RECAPTCHA_SITE_KEY = env.str('RECAPTCHA_SITE_KEY')

GOOGLE_MAPS_API_KEY = env.str('GOOGLE_MAPS_API_KEY')
BASE_URL = env.str('BASE_URL')

TAGS_INPUT_MAPPINGS = {
    'photos.Tag': {
        'field': 'name',
        'create_missing': True
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

from django.db.models import Q,CharField, TextField
from django.db.models.functions import Lower
CharField.register_lookup(Lower, "lower")
TextField.register_lookup(Lower, "lower")
DEFAULT_CHARSET = 'UTF-8'
MINUTES_AGO_HIT_COUNT = 15
IPV6_IP2LOCATION_PATH = "data/IP2LOCATION-LITE-DB1.BIN/IP2LOCATION-LITE-DB1.BIN"
IPV4_IP2LOCATION_PATH = "data/IP2LOCATION-LITE-DB1.IPV6.BIN/IP2LOCATION-LITE-DB1.IPV6.BIN"

IMPORT_EXPORT_USE_TRANSACTIONS = True


MAX_PHOTO_SIZE = 10000000
MAX_PHOTO_SIZE_MB = int(MAX_PHOTO_SIZE / 1000 / 1000)

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_PERMISSIONS = 0o644

#mailing
TESTING_EMAILS = ['neilmackay01@gmail.com', 'juan.crescente@gmail.com', 'yas@yourafricansafari.com']
import datetime 
POST_OFFICE = {
    'MAX_RETRIES': 2,
    'RETRY_INTERVAL': datetime.timedelta(minutes=1),
    'BACKENDS': {
        'django': 'smtp.EmailBackend',
        'default': 'django_ses.SESBackend',
    }
}

EMAIL_USE_TLS = env.str('EMAIL_USE_TLS')
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env.str('EMAIL_PORT')
EMAIL_BACKEND = 'django_ses.SESBackend'
# These are optional -- if they're set as environment variables they won't
# need to be set here as well
AWS_SES_ACCESS_KEY_ID=env.str('AWS_SES_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY=env.str('AWS_SES_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = 'us-west-2'
AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

#ckeditor
CKEDITOR_CONFIGS = {
'default': {
    'toolbar': None, #You can change this based on your requirements.
    'height': 600,
    'disallowedContent': 'img{width,height};'
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]
