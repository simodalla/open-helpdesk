# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from tests.settings_base import *  # noqa

# PyPy compatibility
try:
    from psycopg2ct import compat
    compat.register()
except ImportError:
    pass


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'openhelpdesk_test' + db_suffix,
        'HOST': '127.0.0.1',
        'USER': 'postgres',
    },
}
