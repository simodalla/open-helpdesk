# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

import pytest

from django import VERSION as DJANGO_VERSION
from django.contrib.admin import AdminSite


from helpdesk.admin import TicketAdmin
from helpdesk.models import Ticket

from .helpers import get_mock_request, get_mock_helpdeskuser


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
            'queryset' if DJANGO_VERSION < (1, 6) else 'get_queryset')

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

    def test_field_admin_readonly_content_in_fieldset_if_requester(
            self, mock_get_req_hpu):
        """
        Test that if request.user is a requester and obj isn't None, iterable
        returns by get_fieldsets that contains 'admin_readonly_content'
        """
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(requester=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request(), Mock())
        self.assertIn('admin_readonly_content', fieldeset[0][1]['fields'])

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
            ('tipologies', 'priority', 'admin_readonly_content',
             'related_tickets'), result)

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

    @patch('helpdesk.admin.admin.ModelAdmin.change_view')
    def test_change_view_by_requester_set_messages_in_extra_content(
            self, mock_get_req_hpu):
        helpdesk_user = get_mock_helpdeskuser(requester=True)
        mock_get_req_hpu.return_value = helpdesk_user
        self.ticket_admin.change_view(get_mock_request())



@pytest.fixture
def ticket_admin_change_view(rf_with_helpdeskuser, monkeypatch):
    monkeypatch.setattr('helpdesk.admin.TicketAdmin.get_request_helpdeskuser',
                        lambda self, request: request.user)
    return rf_with_helpdeskuser, 1, TicketAdmin(Ticket, AdminSite)


@pytest.mark.django_db
class TestTicketAdminChangeViewByRequester(object):
    is_requester = True

    @patch('django.contrib.admin.ModelAdmin.change_view')
    def test_view_calls_has_messages_in_extra_content(
            self, mock_cv, ticket_admin_change_view):
        request, object_id, ticket_admin = ticket_admin_change_view
        messages = [1, 2, 3]
        setattr(request.user, 'get_messages_of_ticket',
                lambda ticket_id: messages)
        ticket_admin.change_view(request, object_id)
        mock_cv.assert_called_once_with(request, object_id, form_url='',
                                        extra_context={'messages': messages})

