# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest
pytestmark = pytest.mark.django_db

def test_sitepermission(requester):
    print(requester)