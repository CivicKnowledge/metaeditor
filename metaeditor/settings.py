# -*- coding: utf-8 -*-
import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# TODO: remove it out of here.
SECRET_KEY = os.environ.get('DJANGO_SECRET', None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', False)

TEMPLATE_DEBUG = DEBUG

# Application definition

INSTALLED_APPS = (
    # contrib
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3-d party
    'mptt',
    'social.apps.django_app.default',
    'bootstrap3',
    'url_tools',
    'django_extensions',

    # metaeditor
    'editor',
    'accounts',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'metaeditor.urls'

WSGI_APPLICATION = 'metaeditor.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'metaeditor',
        'USER': 'test',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
'''

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    #os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'url_tools.context_processors.current_url',
)

# python-social-auth
AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',

    # keep django's model backend to allow admin login
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',

    # Associates the current social details with another user account with
    # a similar email address.
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

SOCIAL_AUTH_DISCONNECT_PIPELINE = (
    'social.pipeline.disconnect.get_entries',
    'social.pipeline.disconnect.revoke_tokens',
    'social.pipeline.disconnect.disconnect'
)

# facebook credentials
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY', '')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET', '')

# google credentials
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')

LOGIN_URL = '/'

# ###### logging #######
LOG_ROOT = os.path.join(BASE_DIR, '..', 'logs')
if not os.path.exists(LOG_ROOT):
    os.mkdir(LOG_ROOT)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_ROOT, 'metaeditor.log'),
            'encoding': 'utf-8',
            'maxBytes': 1024 * 1024,  # 1 MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'propagate': False
        }
    }
}

SITE_DOMAIN = 'metaeditor.org'

# ## django-bootstrap3 settings

BOOTSTRAP3 = {
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-8'
}

# ## Editor settings ## #

# wich urls may be included to the documents formset
EDITOR_DOCUMENT_EXTENSIONS = ['.doc', '.docx', '.pdf']

# wich urls may be included to the data files formset
EDITOR_DATAFILE_EXTENSIONS = ['.xls', '.xlsx', '.txt', '.csv']

from local_settings import *

# Parse database configuration from $DATABASE_URL
import dj_database_url
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config()

# TODO: add warning to log if facebook or google credentials do not exist.

if 'test' in sys.argv:
    # run tests using sqlite.
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}
