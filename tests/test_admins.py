# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest

import pytest

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django import VERSION as DJANGO_VERSION
from django.contrib.admin import AdminSite

from helpdesk.admin import TicketAdmin
from helpdesk.models import Ticket, StatusChangesLog

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


@pytest.fixture
def ticket_admin_change_view(rf_with_helpdeskuser, monkeypatch):
    monkeypatch.setattr('helpdesk.admin.TicketAdmin.get_request_helpdeskuser',
                        lambda self, request: request.user)
    return rf_with_helpdeskuser, TicketAdmin(Ticket, AdminSite), 1


class TestTicketAdminByRequester(object):

    @patch('helpdesk.admin.StatusChangesLog', spec_set=StatusChangesLog)
    @patch('django.contrib.admin.ModelAdmin.change_view')
    def test_view_calls_has_messages_and_changelogs_in_extra_content(
            self, mock_cv, mock_sclog, ticket_admin_change_view,):
        request, ticket_admin, object_id = ticket_admin_change_view
        messages = [1, 2, 3]
        statuschangelogs = [1, 2, 3]
        request.user.get_messages_by_ticket = Mock(return_value=messages)
        mock_sclog.objects.filter.return_value.order_by.return_value = (
            statuschangelogs)
        ticket_admin.change_view(request, object_id)
        mock_cv.assert_called_once_with(
            request, object_id, form_url='',
            extra_context={'ticket_messages': messages,
                           'ticket_changelogs': statuschangelogs,
                           'helpdesk_user': request.user})

    @pytest.mark.parametrize(
        'helpdeskuser,expected',
        [('requester', TicketAdmin.list_display),
         ('operator', (TicketAdmin.list_display +
                       TicketAdmin.operator_list_display)),
         ('admin', (TicketAdmin.list_display +
                    TicketAdmin.operator_list_display))])
    def test_custom_list_display(
            self, helpdeskuser, expected, ticket_admin_change_view):
        request, ticket_admin, object_id = ticket_admin_change_view
        setattr(request.user, 'is_{}'.format(helpdeskuser), lambda: True)
        assert ticket_admin.get_list_display(request) == expected

    @pytest.mark.parametrize(
        'helpdeskuser,expected',
        [('requester', TicketAdmin.list_filter),
         ('operator', (TicketAdmin.list_filter +
                       TicketAdmin.operator_list_filter)),
         ('admin', (TicketAdmin.list_filter +
                    TicketAdmin.operator_list_filter))])
    def test_custom_list_filter(
            self, helpdeskuser, expected, ticket_admin_change_view):
        request, ticket_admin, object_id = ticket_admin_change_view
        setattr(request.user, 'is_{}'.format(helpdeskuser), lambda: True)
        assert ticket_admin.get_list_filter(request) == expected

    # def test_custom_readonly_fields_if_obj_is_none(
    #         self, ticket_admin_change_view):
    #     request, ticket_admin, object_id = ticket_admin_change_view
    #     assert (ticket_admin.get_readonly_fields(request) ==
    #             TicketAdmin.readonly_fields)
    #
    # @pytest.mark.parametrize(
    #     'helpdeskuser,expected',
    #     [('requester', {'f1', 'f2'}),
    #      ('operator', TicketAdmin.operator_read_only_fields),
    #      ('admin', TicketAdmin.operator_read_only_fields)])
    # def test_custom_get_readonly_fields_on_ticket_not_closed(
    #         self, helpdeskuser, expected, ticket_admin_change_view):
    #     request, ticket_admin, object_id = ticket_admin_change_view
    #     setattr(request.user, 'is_{}'.format(helpdeskuser), lambda: True)
    #     setattr(ticket_admin, 'get_fieldsets',
    #             lambda r, obj=1: ((None, {'fields': ['f1', 'f2']}),))
    #     mock_ticket = Mock(spec_set=Ticket, pk=1)
    #     mock_ticket.is_closed.return_value = False
    #     # print(True if mock_ticket.is_closed() else False)
    #     assert set(ticket_admin.get_readonly_fields(
    #         request, mock_ticket)) == set(expected)
