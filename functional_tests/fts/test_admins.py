# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.admin.templatetags.admin_urls import admin_urlname

from .base import FunctionalTest
from tests.factories import (
    UserFactory, GroupFactory, CategoryFactory,)
from helpdesk.defaults import HELPDESK_REQUESTERS
from helpdesk.models import Ticket


class AdminTest(FunctionalTest):

    def setUp(self):
        super(AdminTest, self).setUp()
        self.requester = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        self.client.login(username=self.requester.username,
                          password='default')
        self.category = CategoryFactory(tipologies=('tip1', 'tip2', 'tip3',))
        self.create_pre_authenticated_session(self.requester)

    def test_add_booking_type(self):
        """
        <QueryDict: {u'content': [u'<p>sdfksj l&ograve;dfja lskdjfal&ograve;
        </p>'], u'csrfmiddlewaretoken': [u'dQQkQODAudr5iGHoCRFYjCklQTzmYQXD'],
        u'_save': [u'Save'], u'tipologies': [u'2', u'3']}>
        """
        self.browser.get(
            self.get_url(admin_urlname(Ticket._meta, 'add')))
