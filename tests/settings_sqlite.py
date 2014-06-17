# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from tests.settings_base import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
}
