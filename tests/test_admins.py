# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.test import TestCase
from lxml.html import fromstring

from helpdesk.models import Ticket
from .factories import (
    UserFactory, TipologyFactory, CategoryFactory, SiteFactory, RequestersFactory)


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


class AdminTicketByAdminTest(TestCase):
    def setUp(self):
        self.admin = UserFactory(is_superuser=True)
        self.client.login(username=self.admin.username, password='default')
        sites = [SiteFactory() for i in range(0, 2)]
        self.tipologies = [TipologyFactory(category=CategoryFactory(),
                                           sites=sites) for i in range(0, 2)]

    def test_field_requester_is_in_form(self):
        response = self.client.get(
            reverse(admin_urlname(Ticket._meta, 'add')))
        dom = fromstring(response.content)
        self.assertEqual(len(dom.cssselect('#ticket_form #id_requester')), 1)


class AdminTicketByRequesterTest(TestCase):
    def setUp(self):
        self.requester = UserFactory(is_superuser=True)
        self.client.login(username=self.requester.username, password='default')
        sites = [SiteFactory() for i in range(0, 2)]
        self.tipologies = [TipologyFactory(category=CategoryFactory(),
                                           sites=sites) for i in
                           range(0, 2)]

    def test_field_requester_is_in_form(self):
        response = self.client.get(
            reverse(admin_urlname(Ticket._meta, 'add')))
        dom = fromstring(response.content)
        self.assertEqual(len(dom.cssselect('#ticket_form #id_requester')),
                         1)
        print(RequestersFactory())
        # print(NEWUserFactory())
    # def test_add_ticket(self):
    #     print(self.tipologies)
    #     response = self.client.post(
    #         reverse(admin_urlname(Ticket._meta, 'add')),
    #         data={'content': 'helpdesk', '_save': 'Save', 'priority': 1,
    #               'requester':
    #               'tipologies': [str(t.pk) for t in self.tipologies],
    #               'attachment_set-TOTAL_FORMS': '1',
    #               'attachment_set-INITIAL_FORMS': '0',
    #               'attachment_set-MAX_NUM_FORMS': ''}, follow=True)
        # print("**************", response.content)
        # print(response.context['errors'])
        # print(Ticket.objects.all()[0].user)


