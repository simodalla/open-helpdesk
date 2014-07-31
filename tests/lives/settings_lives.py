# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from tests.settings_postgres import *  # noqa

DEBUG = True
INTERNAL_IPS = ("127.0.0.1",)
DEBUG_TOOLBAR_PATCH_SETTINGS = False

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.pages",
    "autocomplete_light",
    "openhelpdesk",
)

try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
