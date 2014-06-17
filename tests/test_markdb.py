# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django.contrib.admin import AdminSite

from helpdesk.admin import TicketAdmin
from helpdesk.models import Ticket


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
        setattr(request.user, 'get_messages_by_ticket',
                lambda ticket_id: messages)
        ticket_admin.change_view(request, object_id)
        mock_cv.assert_called_once_with(request, object_id, form_url='',
                                        extra_context={'messages': messages})