from __future__ import absolute_import, unicode_literals

USE_SOUTH = True


########################
# MAIN DJANGO SETTINGS #
########################

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = ['127.0.0.1']

TIME_ZONE = "Europe/Rome"

USE_TZ = True

LANGUAGE_CODE = "en"
_ = lambda s: s
LANGUAGES = (
    ('en', _('English')),
)

DEBUG = False

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

USE_I18N = True


TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

AUTHENTICATION_BACKENDS = ("mezzanine.core.auth_backends.MezzanineBackend",)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

FILE_UPLOAD_PERMISSIONS = 0o644

SECRET_KEY = "1234567890"
NEVERCACHE_KEY = "0987654321"

#############
# DATABASES #
#############

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "mezzanine_helpdesk",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
    }
}

#########
# PATHS #
#########

import os

# Full filesystem path to the project.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Name of the directory for the project.
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIRNAME

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))

MEDIA_URL = STATIC_URL + "media/"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))

ROOT_URLCONF = 'tests.urls'

TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),
                 os.path.join(PROJECT_ROOT, "../openhelpdesk", "templates"))


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
    # "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    # "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    # "mezzanine.blog",
    # "mezzanine.forms",
    "mezzanine.pages",
    # "mezzanine.galleries",
    "autocomplete_light",
    "openhelpdesk",
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
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "mezzanine.core.request.CurrentRequestMiddleware",
    "mezzanine.core.middleware.RedirectFallbackMiddleware",
    "mezzanine.core.middleware.TemplateForDeviceMiddleware",
    "mezzanine.core.middleware.TemplateForHostMiddleware",
    "mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware",
    "mezzanine.core.middleware.SitePermissionMiddleware",
    # Uncomment the following if using any of the SSL settings:
    # "mezzanine.core.middleware.SSLRedirectMiddleware",
    "mezzanine.pages.middleware.PageMiddleware",
    "mezzanine.core.middleware.FetchFromCacheMiddleware",
)

PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"

#########################
# OPTIONAL APPLICATIONS #
#########################

OPTIONAL_APPS = (
    "debug_toolbar",
    "django_extensions",
    "compressor",
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

####################
# DYNAMIC SETTINGS #
####################

# set_dynamic_settings() will rewrite globals based on what has been
# defined so far, in order to provide some better defaults where
# applicable. We also allow this settings module to be imported
# without Mezzanine installed, as the case may be when using the
# fabfile, where setting the dynamic settings below isn't strictly
# required.
try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())

uid = os.getenv('UID', '')

if uid:
    db_suffix = '_%s' % uid
else:
    db_suffix = ''
