# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from helpdesk.models import Ticket


@pytest.mark.usefixtures('requester_cls')
class TestRequesterAddTicket(WebTest):

    def test_adding_ticket_set_requester_field(self):
        """
        Test that adding new ticket, the field requester is setted with
        logged user.
        """
        index = self.app.get(
            reverse(admin_urlname(Ticket._meta, 'add')), user=self.requester)
        print(index.form)
        print(id(self.requester))

    def test_admin_1001(self):
        response = self.app.get(
            reverse(admin_urlname(Ticket._meta, 'add')), user=self.requester)
        print(response.form)
        print(id(self.requester))

    def test_admin_1002(self):
        index = self.app.get(
            reverse(admin_urlname(Ticket._meta, 'add')), user=self.requester)
        print(index.form)
        print(id(self.requester))