# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django.core.urlresolvers import reverse
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.test import TestCase
from lxml.html import fromstring

from helpdesk.models import Ticket
from helpdesk.defaults import (HELPDESK_REQUESTERS, HELPDESK_OPERATORS,
                               HELPDESK_ADMINS)
from helpdesk.admin import TicketAdmin
from .factories import (
    UserFactory, TipologyFactory, CategoryFactory, SiteFactory, GroupFactory)


class AdminCategoryAndTipologyTest(TestCase):
    def setUp(self):
        self.admin = UserFactory(is_superuser=True)
        self.client.login(username=self.admin.username, password='default')
        self.tipology = TipologyFactory(
            category=CategoryFactory(),
            sites=[SiteFactory() for i in range(0, 2)])

    def test_view_site_from_tipology_changelist_view(self):
        response = self.client.get(
            reverse(admin_urlname(self.tipology._meta, 'changelist')))
        dom = fromstring(response.content)
        view_site_links = dom.cssselect('a.view_site')
        self.assertEqual(len(view_site_links), self.tipology.sites.count())
        response = self.client.get(view_site_links[0].get('href'))
        self.assertEqual(response.status_code, 200)
        dom = fromstring(response.content)
        self.assertEqual(
            len(dom.cssselect('div.result-list table tbody tr')), 1)

    def test_view_category_from_tipology_changelist_view(self):
        response = self.client.get(
            reverse(admin_urlname(self.tipology._meta, 'changelist')))
        dom = fromstring(response.content)
        view_category_links = dom.cssselect('a.view_category')
        self.assertEqual(len(view_category_links), 1)
        response = self.client.get(view_category_links[0].get('href'))
        self.assertEqual(response.status_code, 200)
        dom = fromstring(response.content)
        self.assertEqual(
            len(dom.cssselect('div.result-list table tbody tr')), 1)

    def test_view_tipology_from_category_changelist_view(self):
        TipologyFactory(category=self.tipology.category)
        response = self.client.get(
            reverse(admin_urlname(self.tipology.category._meta, 'changelist')))
        dom = fromstring(response.content)
        view_tipology_links = dom.cssselect('a.view_tipology')
        self.assertEqual(len(view_tipology_links), 2)
        for link in view_tipology_links:
            response = self.client.get(link.get('href'))
            self.assertEqual(response.status_code, 200)
            dom = fromstring(response.content)
            self.assertEqual(
                len(dom.cssselect('div.result-list table tbody tr')), 1)


class AdminTicketByRequestersTest(TestCase):
    def setUp(self):
        self.user = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        self.client.login(username=self.user.username, password='default')
        sites = [SiteFactory() for i in range(0, 2)]
        self.tipologies = [TipologyFactory(category=CategoryFactory(),
                                           sites=sites) for i in
                           range(0, 2)]

    def test_field_requester_not_in_form(self):
        ticket_admin = TicketAdmin(Ticket, AdminSite)
        mock = Mock()
        mock.user = self.user
        print(ticket_admin)


        response = self.client.get(
            reverse(admin_urlname(Ticket._meta, 'add')))
        dom = fromstring(response.content)
        self.assertEqual(len(dom.cssselect('#ticket_form #id_requester')), 0)


class AdminTicketByOperatorsTest(TestCase):
    def setUp(self):
        self.user = UserFactory(
            groups=[GroupFactory(name=HELPDESK_OPERATORS[0],
                                 permissions=list(
                                     HELPDESK_OPERATORS[1]))])
        self.client.login(username=self.user.username,
                          password='default')
        sites = [SiteFactory() for i in range(0, 2)]
        self.tipologies = [TipologyFactory(category=CategoryFactory(),
                                           sites=sites) for i in
                           range(0, 2)]

    def test_field_requester_is_in_form(self):
        response = self.client.get(
            reverse(admin_urlname(Ticket._meta, 'add')))
        dom = fromstring(response.content)
        self.assertEqual(
            len(dom.cssselect('#ticket_form #id_requester')), 1)


class AdminTicketByAdminsTest(TestCase):
    def setUp(self):
        self.user = UserFactory(
            groups=[GroupFactory(name=HELPDESK_ADMINS[0],
                                 permissions=list(HELPDESK_ADMINS[1]))])
        self.client.login(username=self.user.username, password='default')
        sites = [SiteFactory() for i in range(0, 2)]
        self.tipologies = [TipologyFactory(category=CategoryFactory(),
                                           sites=sites) for i in range(0, 2)]

    def test_field_requester_is_in_form(self):
        response = self.client.get(
            reverse(admin_urlname(Ticket._meta, 'add')))
        dom = fromstring(response.content)
        self.assertEqual(len(dom.cssselect('#ticket_form #id_requester')), 1)
