# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django_webtest import WebTestMixin


@pytest.fixture
def app(request):
    """Fixture for use Webtest (django-webtest)"""
    wt = WebTestMixin()
    wt._patch_settings()
    request.addfinalizer(wt._unpatch_settings)
    wt.renew_app()
    return wt.app
