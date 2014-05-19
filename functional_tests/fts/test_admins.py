# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.test import TestCase, LiveServerTestCase

from .base import FunctionalTest
from tests.factories import (
    UserFactory, GroupFactory, TipologyFactory, CategoryFactory,
    HELPDESK_ISSUE_MAKERS)
from helpdesk.models import Ticket, Category, Tipology


class AdminTest(FunctionalTest):

    def setUp(self):
        super(AdminTest, self).setUp()
        self.issue_maker = UserFactory(groups=(
            GroupFactory(name=HELPDESK_ISSUE_MAKERS,
                         permissions=('helpdesk.add_ticket',
                                      'helpdesk.change_ticket',)),))
        self.client.login(username=self.issue_maker.username,
                          password='default')
        self.create_pre_authenticated_session(self.issue_maker)

    def test_add_booking_type(self):
        self.browser.get(
            self.get_url(admin_urlname(Ticket._meta, 'changelist')))
        self.assertEqual(1, 1)

    #
    # def test_1(self):
    #     CategoryFactory(tipologies=('tip1', 'tip2', 'tip3',))
    #     print(Category.objects.all())
    #     print(Tipology.objects.all())
