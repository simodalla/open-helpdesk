
from __future__ import absolute_import, unicode_literals
import os
from django.utils.translation import ugettext_lazy as _

########################
# MAIN DJANGO SETTINGS #
########################

SECRET_KEY = "1234567890"
NEVERCACHE_KEY = "0987654321"

ALLOWED_HOSTS = ['127.0.0.1']

TIME_ZONE = 'Europe/Rome'

USE_TZ = True

LANGUAGE_CODE = "en"

LANGUAGES = (
    ('en', _('English')),
)

DEBUG = False

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

USE_I18N = True
USE_L10N = True


AUTHENTICATION_BACKENDS = ("mezzanine.core.auth_backends.MezzanineBackend",)

FILE_UPLOAD_PERMISSIONS = 0o644


#############
# DATABASES #
#############
uid = os.getenv('UID', 0)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        'NAME': 'test_openhelpdesk_{}'.format(uid),
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "",
    }
}


#########
# PATHS #
#########

PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_APP = os.path.basename(PROJECT_APP_PATH)
PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_APP

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))

MEDIA_URL = STATIC_URL + "media/"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))

ROOT_URLCONF = "%s.urls" % PROJECT_APP

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),)


################
# APPLICATIONS #
################

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "autocomplete_light",
    "openhelpdesk",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.pages",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    "mezzanine.conf.context_processors.settings",
    "mezzanine.pages.context_processors.page",
)

MIDDLEWARE_CLASSES = (
    "mezzanine.core.middleware.UpdateCacheMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "mezzanine.core.request.CurrentRequestMiddleware",
    "mezzanine.core.middleware.RedirectFallbackMiddleware",
    # "mezzanine.core.middleware.TemplateForDeviceMiddleware",
    # "mezzanine.core.middleware.TemplateForHostMiddleware",
    # "mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware",
    "mezzanine.core.middleware.SitePermissionMiddleware",
    # Uncomment the following if using any of the SSL settings:
    # "mezzanine.core.middleware.SSLRedirectMiddleware",
    "mezzanine.pages.middleware.PageMiddleware",
    # "mezzanine.core.middleware.FetchFromCacheMiddleware",
)

PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"

#########################
# OPTIONAL APPLICATIONS #
#########################

OPTIONAL_APPS = (
    "debug_toolbar",
    PACKAGE_NAME_GRAPPELLI,
)

##################
# LOCAL SETTINGS #
##################

# f = os.path.join(PROJECT_APP_PATH, "local_settings.py")
# if os.path.exists(f):
#     exec(open(f, "rb").read())


####################
# DYNAMIC SETTINGS #
####################

try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
