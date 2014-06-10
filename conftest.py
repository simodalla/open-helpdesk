# -*- coding: utf-8 -*-
import os

import pytest

from django.conf import settings


from six.moves import cStringIO


def pytest_configure():
    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


@pytest.fixture(scope="module")
def stringios():
    return cStringIO(), cStringIO()