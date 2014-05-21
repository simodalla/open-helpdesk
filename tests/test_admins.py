# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest

try:
    from unittest.mock import patch, Mock, call
except ImportError:
    from mock import patch, Mock, call

from django.core.urlresolvers import reverse
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.test import TestCase
from lxml.html import fromstring

from helpdesk.models import Ticket, HelpdeskUser
from helpdesk.defaults import (HELPDESK_REQUESTERS)
from helpdesk.admin import TicketAdmin
from .factories import (
    UserFactory, TipologyFactory, CategoryFactory, SiteFactory, GroupFactory)


class CategoryAndTipologyTest(TestCase):
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


@patch('helpdesk.admin.HelpdeskUser', autospec=True)
class TicketFieldsetTest(unittest.TestCase):

    def test_field_requester_not_in_form_if_requester_in_request(
            self, mock_user):
        request_mock = Mock(user=Mock(pk=1))
        mock_helpdesk_user = Mock(spec_set=HelpdeskUser)
        mock_helpdesk_user.is_requester.return_value = True
        mock_user.objects.get.return_value = mock_helpdesk_user
        ticket_admin = TicketAdmin(Ticket, AdminSite)
        fieldeset = ticket_admin.get_fieldsets(request_mock)
        mock_user.objects.get.assert_called_once_with(pk=1)
        mock_helpdesk_user.is_requester.assert_called_once_with()
        self.assertFalse(mock_helpdesk_user.is_operator.called)
        self.assertFalse(mock_helpdesk_user.is_admin.called)
        self.assertNotIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_operator_in_request(
            self, mock_user):
        request_mock = Mock(user=Mock(pk=1))
        mock_helpdesk_user = Mock(spec_set=HelpdeskUser)
        mock_helpdesk_user.is_requester.return_value = False
        mock_helpdesk_user.is_operator.return_value = True
        mock_user.objects.get.return_value = mock_helpdesk_user
        ticket_admin = TicketAdmin(Ticket, AdminSite)
        fieldeset = ticket_admin.get_fieldsets(request_mock)
        mock_user.objects.get.assert_called_once_with(pk=1)
        mock_helpdesk_user.is_requester.assert_called_once_with()
        mock_helpdesk_user.is_operator.assert_called_once_with()
        self.assertFalse(mock_helpdesk_user.is_admin.called)
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_admin_in_request(
            self, mock_user):
        request_mock = Mock(user=Mock(pk=1))
        mock_helpdesk_user = Mock(spec_set=HelpdeskUser)
        mock_helpdesk_user.is_requester.return_value = False
        mock_helpdesk_user.is_operator.return_value = False
        mock_helpdesk_user.is_admin.return_value = True
        mock_user.objects.get.return_value = mock_helpdesk_user
        ticket_admin = TicketAdmin(Ticket, AdminSite)
        fieldeset = ticket_admin.get_fieldsets(request_mock)
        mock_user.objects.get.assert_called_once_with(pk=1)
        mock_helpdesk_user.is_requester.assert_called_once_with()
        mock_helpdesk_user.is_operator.assert_called_once_with()
        mock_helpdesk_user.is_admin.assert_called_once_with()
        self.assertIn('requester', fieldeset[0][1]['fields'])


class TicketByRequesterTest(TestCase):
    def setUp(self):
        self.user = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        # self.user = UserFactory(
        #     groups=[GroupFactory(name=HELPDESK_ADMINS[0],
        #                          permissions=list(HELPDESK_ADMINS[1]))])
        self.client.login(username=self.user.username, password='default')
        self.category = CategoryFactory(tipologies=('tip1', 'tip2'))
        self.post_data = {'content': 'helpdesk_content',
                          'tipologies': [str(t.pk) for t
                                         in self.category.tipologies.all()],
                          'priority': 1}

    def test_add_ticket(self):
        response = self.client.post(
            reverse(admin_urlname(Ticket._meta, 'add')), data=self.post_data)
        print(response.content)
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.user.pk, self.user.pk)
        self.assertEqual(ticket.requester.pk, self.user.pk)



