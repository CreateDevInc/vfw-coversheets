"""
Django settings for vfw project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf import global_settings
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '' # removed to commit to github

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

ADMINS = (('Anthony-vfw', 'lockes5hadow@gmail.com'),)
SERVER_EMAIL = 'coversheets@vs-az.com'

# Application definition

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'coversheets',
    'cities_light',
    'bootstrap3',
    'sorl.thumbnail',
    'cuser',
    'reversion',
    # 'reversion_compare',
    'lightbox',
    'jquery',
    'relatedwidget',
    'bootstrap3_datetime',
    'debug_toolbar',
    'multi_email_field',
    'datetimewidget',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cuser.middleware.CuserMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

SITE_ID = 1

ROOT_URLCONF = 'vfw.urls'

WSGI_APPLICATION = 'vfw.wsgi.application'

MAX_UPLOAD_SIZE = "52428800"
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


from django.contrib.sites.models import Site
#new_site = Site.objects.create(domain='brozano.com', name='brozano.com')
#print new_site.id


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_INPUT_FORMATS = (
    '%H:%M:%S',     # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M',        # '14:30'
    '%I:%M %p'      # '11:30 AM'
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'C:\\Users\\Anthony\\PycharmProjects\\vfw\\collected_staticfiles'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT = '/media/'

MEDIA_URL = '/media/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'django.core.context_processors.static'
)

BOOTSTRAP_ADMIN_SIDEBAR_MENU = True

THUMBNAIL_HIGH_RESOLUTION = True

## suit

SUIT_CONFIG = {
    'SEARCH_URL': '/admin/coversheets/job/',
    'ADMIN_NAME': '<img src="/static/img/v_only.png"> Valley Services of Arizona',
    'HEADER_TIME_FORMAT': 'P',
    'MENU_ICONS': {
        'coversheets': 'icon-list',
        'auth': 'icon-lock',
    },
    'MENU_EXCLUDE': {'cities_light', },
    'MENU': ({'app': 'coversheets', 'icon': 'icon-list', 'models': ('job', 'adjuster', 'album', 'calltype', 'referraltype')},
             {'app': 'auth', 'label': 'Users'},
             {'label': 'Reports', 'url': '/coversheets/reports'}
    )
}
TIME_ZONE = 'America/Phoenix'

# ADD_REVERSION_ADMIN=True

## Cities Light

CITIES_LIGHT_INCLUDE_COUNTRIES = ['US', 'CA']
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en']

## LightBox

LIGHTBOX_MODEL = 'Album'
LIGHTBOX_APP = 'coversheets'


## Email config
EMAIL_BACKEND = 'django_ses.SESBackend'

DEFAULT_FROM_EMAIL = ''
DEFAULT_TO_EMAIL = ''

# it's not polite to tell secrets 
AWS_SES_ACCESS_KEY_ID = ''
AWS_SES_SECRET_ACCESS_KEY = ''

AWS_SES_REGION_NAME = 'us-west-2'
AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

## coversheets
SEND_EMAIL_NOTIFCATIONS = True

## django-money
CURRENCIES = ('USD',)