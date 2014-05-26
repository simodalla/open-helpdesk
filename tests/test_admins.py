# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest
from copy import deepcopy

try:
    from unittest.mock import patch, Mock, call
except ImportError:
    from mock import patch, Mock, call

import pytest

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


def get_mock_helpdeskuser(requester=False, operator=False, admin=False,
                          is_superuser=False):
    mock_helpdesk_user = Mock()
    mock_helpdesk_user.is_superuser = is_superuser
    mock_helpdesk_user.is_requester.return_value = requester
    mock_helpdesk_user.is_operator.return_value = operator
    mock_helpdesk_user.is_admin.return_value = admin
    return mock_helpdesk_user


def get_mock_request(user_pk=1):
    request_mock = Mock(user=Mock(pk=user_pk))
    return request_mock


class TicketTest(unittest.TestCase):

    def setUp(self):
        self.ticket_admin = TicketAdmin(Ticket, AdminSite)

    @patch('helpdesk.admin.HelpdeskUser.objects.get',
           return_value=get_mock_helpdeskuser())
    def test_get_request_helpdeskuser(self, mock_get):
        request = get_mock_request(1)
        user = self.ticket_admin.get_request_helpdeskuser(request)
        mock_get.assert_called_once_with(pk=1)
        self.assertEqual(user, mock_get.return_value)


@patch('helpdesk.admin.TicketAdmin.get_request_helpdeskuser')
class TicketMethodsByRequesterTypeTest(unittest.TestCase):

    def setUp(self):
        self.ticket_admin = TicketAdmin(Ticket, AdminSite)
        self.fake_pk = 1

    def test_field_requester_not_in_form_if_requester_in_request(
            self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(requester=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertNotIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_operator_in_request(
            self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(
            operator=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_admin_in_request(
            self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(admin=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_superuser_in_request(
            self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(is_superuser=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_list_filter_if_requester_in_request(self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(requester=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter, result)

    def test_list_filter_if_operator_in_request(self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(operator=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter + ['requester', 'assignee'], result)

    def test_list_filter_if_admin_in_request(self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(admin=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter + ['requester', 'assignee'], result)

    def test_list_filter_if_superuser_in_request(self, mock_get):
        mock_get.return_value = get_mock_helpdeskuser(is_superuser=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter + ['requester', 'assignee'],
                             result)


class FunctionalTicketByRequesterTest(TestCase):
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
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.requester.pk, self.user.pk)
