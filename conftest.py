# -*- coding: utf-8 -*-
import os

import pytest

from django.conf import settings

from six.moves import cStringIO


def pytest_configure():
    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


@pytest.fixture(scope='module')
def stringios():
    return cStringIO(), cStringIO()


def helpdesker(helpdesker_conf):
    from django.contrib.sites.models import Site
    import helpdesk.defaults
    from tests.factories import UserFactory, GroupFactory
    from tests.settings import SITE_ID

    helpdesker_conf = getattr(helpdesk.defaults, helpdesker_conf, None)
    if not helpdesker_conf:
        return None
    user = UserFactory(
        groups=[GroupFactory(name=helpdesker_conf[0],
                             permissions=list(helpdesker_conf[1]))])
    sp = user.sitepermissions.create(user=user)
    sp.sites.add(Site.objects.get(pk=SITE_ID))
    return user


@pytest.fixture(scope='module')
def requester():
    return helpdesker('HELPDESK_REQUESTERS')


@pytest.fixture(scope='module')
def operator():
    return helpdesker('HELPDESK_OPERATORS')


@pytest.fixture(scope='class')
def requester_cls(request, requester):
    setattr(request.cls, 'requester', requester)
