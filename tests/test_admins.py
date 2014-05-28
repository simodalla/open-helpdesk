# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django import VERSION as django_version
from django.core.urlresolvers import reverse
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.test import TestCase
from lxml.html import fromstring

from helpdesk.models import Ticket
from helpdesk.defaults import (HELPDESK_REQUESTERS,
                               HELPDESK_TICKET_MAX_TIPOLOGIES)
from helpdesk.admin import TicketAdmin
from .factories import (
    UserFactory, TipologyFactory, CategoryFactory, SiteFactory, GroupFactory,
    TicketFactory)
from .helpers import get_mock_request, get_mock_helpdeskuser, AdminTestMixin


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


class TicketTest(unittest.TestCase):

    def setUp(self):
        self.ticket_admin = TicketAdmin(Ticket, AdminSite)

    @patch('helpdesk.admin.HelpdeskUser.objects.get',
           return_value=get_mock_helpdeskuser())
    def test_get_request_helpdeskuser(self, mock_get_req_hpu):
        user = self.ticket_admin.get_request_helpdeskuser(get_mock_request(1))
        mock_get_req_hpu.assert_called_once_with(pk=1)
        self.assertEqual(user, mock_get_req_hpu.return_value)


@patch('helpdesk.admin.TicketAdmin.get_request_helpdeskuser')
class TicketMethodsByRequesterTypeTest(unittest.TestCase):

    def setUp(self):
        self.ticket_admin = TicketAdmin(Ticket, AdminSite)
        self.fake_pk = 1

    def get_queryset_to_patch(self):
        return 'django.contrib.admin.ModelAdmin.{}'.format(
            'queryset' if django_version < (1, 6) else 'get_queryset')

    def test_field_requester_not_in_form_if_requester_in_request(
            self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(requester=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertNotIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_operator_in_request(
            self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(
            operator=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_admin_in_request(
            self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(admin=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_superuser_in_request(
            self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(superuser=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_list_filter_if_requester_in_request(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(requester=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter, result)

    def test_list_filter_if_operator_in_request(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(operator=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter + ['requester', 'assignee'], result)

    def test_list_filter_if_admin_in_request(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(admin=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter + ['requester', 'assignee'], result)

    def test_list_filter_if_superuser_in_request(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(superuser=True)
        list_filter = list(self.ticket_admin.list_filter)
        result = self.ticket_admin.get_list_filter(get_mock_request())
        self.assertListEqual(list_filter + ['requester', 'assignee'],
                             result)

    def test_empty_readonly_fields_if_obj_is_none(self, mock_get_req_hpu):
        result = self.ticket_admin.get_readonly_fields(get_mock_request())
        self.assertEqual(tuple(), result)

    def test_empty_readonly_fields_if_operator_in_request(self,
                                                          mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(operator=True)
        result = self.ticket_admin.get_readonly_fields(
            get_mock_request(), obj=Mock(spec_set=Ticket, pk=self.fake_pk))
        self.assertEqual(tuple(), result)

    def test_empty_readonly_fields_if_admin_in_request(self,
                                                       mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(admin=True)
        result = self.ticket_admin.get_readonly_fields(
            get_mock_request(), obj=Mock(spec_set=Ticket, pk=self.fake_pk))
        self.assertEqual(tuple(), result)

    def test_empty_readonly_fields_if_superuser_in_request(self,
                                                           mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(superuser=True)
        result = self.ticket_admin.get_readonly_fields(
            get_mock_request(), obj=Mock(spec_set=Ticket, pk=self.fake_pk))
        self.assertEqual(tuple(), result)

    def test_empty_readonly_fields_if_requester_in_request(self,
                                                           mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(requester=True)
        result = self.ticket_admin.get_readonly_fields(
            get_mock_request(), obj=Mock(spec_set=Ticket, pk=self.fake_pk))
        self.assertEqual(
            ('tipologies', 'priority', 'content', 'related_tickets'), result)

    def test_queryset_is_not_filterd_if_is_operator(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(operator=True)
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        self.assertTrue(result is qs)

    def test_queryset_is_not_filterd_if_is_admin(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(admin=True)
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        self.assertTrue(result is qs)

    def test_queryset_is_not_filterd_if_is_superuser(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(superuser=True)
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        self.assertTrue(result is qs)

    def test_queryset_is_not_filterd_if_is_requester(self, mock_get_req_hpu):
        helpdesk_user = get_mock_helpdeskuser(requester=True)
        mock_get_req_hpu.return_value = helpdesk_user
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        qs.filter.assert_called_once_with(requester=helpdesk_user)
        self.assertFalse(result is qs)


class FunctionalTicketByRequesterTest(AdminTestMixin, TestCase):
    def setUp(self):
        self.requester = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        self.client.login(username=self.requester.username, password='default')
        tipology_names = ['tip{}'.format(i) for i
                          in range(0, HELPDESK_TICKET_MAX_TIPOLOGIES-1)]
        self.category = CategoryFactory(tipologies=tipology_names)
        self.post_data = {'content': 'helpdesk_content',
                          'tipologies': self.category.tipology_pks,
                          'priority': 1}

    def test_adding_ticket_set_requester_field(self):
        """
        Test that adding new ticket, the field requester is setted with
        logged user.
        """
        self.client.post(
            reverse(admin_urlname(Ticket._meta, 'add')), data=self.post_data)
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.requester.pk, self.requester.pk)

    def test_changelist_view_is_filtered(self):
        """
        Test that the changelist is filtered by tickets with requester's field
        matching to logged user.
        """
        n = 3
        for user in [self.requester, UserFactory(
                groups=self.requester.groups.all())]:
            [TicketFactory(requester=user,
                           tipologies=self.category.tipologies.all())
             for i in range(0, n)]
        response = self.client.get(self.get_url(Ticket, 'changelist'))
        if django_version < (1, 6):
            tickets_pks = response.context['cl'].result_list.values_list(
                'pk', flat=True)
        else:
            tickets_pks = response.context['cl'].queryset.values_list(
                'pk', flat=True)
        self.assertEqual(len(tickets_pks), n)
        self.assertEqual(
            set(tickets_pks),
            set(self.requester.requested_tickets.values_list('pk', flat=True)))

    def test_form_with_less_tipologies_fields_is_validate(self):
        assert (len(self.post_data['tipologies'])
                < HELPDESK_TICKET_MAX_TIPOLOGIES)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertRedirects(response, self.get_url(Ticket, 'changelist'))

    def test_form_with_equals_tipologies_fields_is_validate(self):
        tipology_names = ['tip{}'.format(i) for i
                          in range(0, HELPDESK_TICKET_MAX_TIPOLOGIES)]
        category = CategoryFactory(tipologies=tipology_names)
        self.post_data['tipologies'] = category.tipology_pks
        assert (len(self.post_data['tipologies'])
                == HELPDESK_TICKET_MAX_TIPOLOGIES)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertRedirects(response, self.get_url(Ticket, 'changelist'))

    def test_form_with_more_tipologies_fields_is_not_validate(self):
        tipology_names = ['tip{}'.format(i) for i
                          in range(0, HELPDESK_TICKET_MAX_TIPOLOGIES + 1)]
        category = CategoryFactory(tipologies=tipology_names)
        self.post_data['tipologies'] = category.tipology_pks
        assert (len(self.post_data['tipologies'])
                > HELPDESK_TICKET_MAX_TIPOLOGIES)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['adminform'].form
        self.assertIn('tipologies', form.keys())
        # self.assertEqual()
        # [error for errors in response.context['errors'] for error in errors]
        # self.assertEqual()
        # self.assertFormError(response, response.context['adminform'].form,
        #                      'tipologies',
        #                      'Too many tipologies selected. You can select a maximum of 3')

    def test_for_fieldset_object(self):
        self.client.get(self.get_url(Ticket, 'add'))
        t = TicketFactory(requester=self.requester,
                          tipologies=self.category.tipologies.all())
        self.client.get(self.get_url(Ticket, 'change', args=(t.pk,)))
