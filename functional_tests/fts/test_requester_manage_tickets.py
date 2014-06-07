# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.sites.models import Site

from .base import FunctionalTest
from tests.factories import (
    UserFactory, GroupFactory, CategoryFactory, TipologyFactory)
from helpdesk.defaults import HELPDESK_REQUESTERS
from helpdesk.models import Ticket


class RequesterTicketsTest(FunctionalTest):

    def setUp(self):
        super(RequesterTicketsTest, self).setUp()
        self.requester = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        self.client.login(username=self.requester.username,
                          password='default')
        self.category = CategoryFactory()
        site = Site.objects.get(pk=1)
        self.tipologies = [
            TipologyFactory(sites=(site,), category=self.category)
            for i in range(0, 2)]
        self.create_pre_authenticated_session(self.requester)

    def test_add_booking_type(self):
        """
        <QueryDict: {u'content': [u'<p>sdfksj l&ograve;dfja lskdjfal&ograve;
        </p>'], u'csrfmiddlewaretoken': [u'dQQkQODAudr5iGHoCRFYjCklQTzmYQXD'],
        u'_save': [u'Save'], u'tipologies': [u'2', u'3']}>
        """
        self.browser.get(
            self.get_url(admin_urlname(Ticket._meta, 'add')))
        self.browser.find_element_by_css_selector(
            "#id_tipologies_from option[value='{}']".format(
                self.tipologies[0].pk)).click()
        self.browser.find_element_by_css_selector(
            '#id_tipologies_add_link').click()
        self.browser.find_element_by_name('_save').click()
        import ipdb
        ipdb.set_trace()
