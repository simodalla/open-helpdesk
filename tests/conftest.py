
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest


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