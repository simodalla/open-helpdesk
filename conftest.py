# -*- coding: utf-8 -*-
import os

import pytest
from django.conf import settings

from six.moves import cStringIO

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


def pytest_configure():
    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings_postgres'


def pytest_addoption(parser):
    parser.addoption('--livetest', action='store_true',
                     help='run live  tests')


def pytest_runtest_setup(item):
    if ('livetest' in item.keywords and
            not item.config.getoption('--livetest')):
        pytest.skip('need --livetest option to run')
    # dynamically set DJANGO_SETTINGS_MODULE if module of current test (item)
    # is 'tests.lives'
    if item.module.__package__ == 'tests.lives':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings_lives'


@pytest.fixture(scope='module')
def stringios():
    return cStringIO(), cStringIO()


def helpdesker(helpdesker_conf):
    from django.contrib.sites.models import Site
    import helpdesk.defaults
    from tests.factories import UserFactory, GroupFactory
    from tests.settings_base import SITE_ID

    helpdesker_conf = getattr(helpdesk.defaults, helpdesker_conf, None)
    if not helpdesker_conf:
        return None
    user = UserFactory(
        username=helpdesker_conf[0].rstrip('s'),
        groups=[GroupFactory(name=helpdesker_conf[0],
                             permissions=list(helpdesker_conf[1]))])
    sp = user.sitepermissions.create(user=user)
    sp.sites.add(Site.objects.get(pk=SITE_ID))
    return user


@pytest.fixture
def requester():
    return helpdesker('HELPDESK_REQUESTERS')


@pytest.fixture
def operator():
    return helpdesker('HELPDESK_OPERATORS')


@pytest.fixture(scope='class')
def requester_cls(request):
    setattr(request.cls, 'requester', helpdesker('HELPDESK_REQUESTERS'))


class ModelAdminUtil(object):
    def __init__(self):
        self.rf = None
        self.user = None
        self.request = None
        self.model_admin = None
        self.obj = None
        self.form = Mock()
        self.qs = None

    def get(self, path):
        request = self.rf.get(path)
        request.user = self.user
        return request

    def post(self, path, data=None):
        request = self.rf.post(path, data)
        request.user = self.user
        return request


@pytest.fixture
def model_admin_util(rf):
    from helpdesk.models import HelpdeskUser
    from django.db.models.query import QuerySet

    mau = ModelAdminUtil()
    mau.rf = rf
    mau.user = Mock(spec_set=HelpdeskUser, name='helpdeskuser')
    mau.qs = Mock(spec_set=QuerySet, name='queryset')
    mau.request = mau.get('/admin/fake/')

    return mau