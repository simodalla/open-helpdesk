# -*- coding: utf-8 -*-
import os

import pytest

from django.conf import settings


def pytest_configure():
    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings_postgres'


def pytest_addoption(parser):
    parser.addoption('--livetest', action='store_true',
                     help='run live tests')


def pytest_runtest_setup(item):
    if ('livetest' in item.keywords and
            not item.config.getoption('--livetest')):
        pytest.skip('need --livetest option to run')
