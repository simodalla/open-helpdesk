# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django_webtest import WebTest

from helpdesk.models import Ticket
from helpdesk.defaults import HELPDESK_REQUESTERS

from ..factories import UserFactory, GroupFactory


# pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('requester_cls')
class TestRequestAddTicket(WebTest):
    def test_admin(self):
        from django.contrib.auth.models import User
        print(User.objects.all())
        # print(Site.objects.all())
        # requester = UserFactory(
        #     groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
        #                          permissions=list(HELPDESK_REQUESTERS[1]))])
        # print(admin_urlname(Ticket._meta, 'add'))
        index = self.app.get(
            reverse(admin_urlname(Ticket._meta, 'add')), user=self.requester)
        print(index.form)
        print(id(self.requester))
        # import pytest
        # pytest.set_trace()

    def test_admin_2(self):
        from django.contrib.auth.models import User
        print(User.objects.all())
        # print(Site.objects.all())
        # requester = UserFactory(
        #     groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
        #                          permissions=list(HELPDESK_REQUESTERS[1]))])
        # print(admin_urlname(Ticket._meta, 'add'))
        index = self.app.get(
            reverse(admin_urlname(Ticket._meta, 'add')), user=self.requester)
        print(index.form)
        print(id(self.requester))
        # import pytest

# @pytest.mark.django_db
#
# class TestAaa():
#     def test_1(self):
#         print(self.requester)