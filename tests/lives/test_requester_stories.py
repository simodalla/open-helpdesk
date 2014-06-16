# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

pytestmark = pytest.mark.django_db

from django.contrib.sites.models import Site
from mezzanine.core.models import SitePermission


def test_1001(browser_requestered, settings):
    print(settings.DATABASES)
    browser, requester = browser_requestered
    browser.get('admin:helpdesk_ticket_add')
    print("*************************************")




def test_1002(browser_requestered):
    browser, requester = browser_requestered
    browser.get('admin:helpdesk_ticket_add')
    print("*************************************")
