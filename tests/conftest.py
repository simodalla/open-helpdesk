
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from six.moves import cStringIO


@pytest.fixture(scope='module')
def stringios():
    return cStringIO(), cStringIO()


@pytest.fixture(scope='module')
def demo():
    class Demo(object):
        pass
    return Demo()


@pytest.fixture(scope='module')
def requester():
    from tests.factories import UserFactory, GroupFactory
    from helpdesk.defaults import HELPDESK_REQUESTERS
    user = UserFactory(groups=[GroupFactory(name=HELPDESK_REQUESTERS[0])])
    return user


@pytest.fixture
def rf_with_helpdeskuser(request, rf):
    rf.user = None
    if getattr(request, 'cls', None):
        class HelpdeskUser(object):
            def is_requester(self):
                return getattr(request.cls, 'is_requester', False)

            def is_operator(self):
                return getattr(request.cls, 'is_operator', False)

            def is_admin(self):
                return getattr(request.cls, 'is_admin', False)
        rf.user = HelpdeskUser()
    return rf

