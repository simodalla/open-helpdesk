# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django.test import TestCase
from helpdesk.models import Ticket
from helpdesk.views import OpenTicketView

from .helpers import TestViewHelper


class OpenTicketViewTest(TestViewHelper, TestCase):

    view_class = OpenTicketView

    def setUp(self):
        super(OpenTicketViewTest, self).setUp()
        self.mock_user = Mock(name='request.user')

    def tearDown(self):
        self.mock_user.reset_mock()

    @patch('helpdesk.views.messages', autospec=True)
    @patch('helpdesk.views.Ticket.objects.get',
           side_effect=Ticket.DoesNotExist)
    def test_get_redirect_url_raise_doesnotexist_excpetion(self, mock_get,
                                                           mock_messages):
        """
        Test that get_get_redirect return admin ticket changelist url
        and messages.error is called with proper message.
        """
        fake_ticket_pk = 1
        request = self.build_request(user=self.mock_user)
        # request = self.build_request(user=UserFactory())
        view = self.build_view(request)
        url = view.get_redirect_url(pk=fake_ticket_pk)
        self.assertEqual(url, '/admin/helpdesk/ticket/')
        mock_messages.error.assert_called_once_with(
            request, 'An error occurs. Ticket n.{} does not exist.'.format(
                fake_ticket_pk))

    @patch('helpdesk.views.messages', autospec=True)
    @patch('helpdesk.views.Ticket.objects.get')
    def test_open_in_get_redirect_url_raise_excpetion(self, mock_get,
                                                      mock_messages):
        """
        Test that get_get_redirect return admin ticket changelist url
        and messages.error is called with proper message.
        """
        fake_ticket_pk = 1
        fake_open_error = 'Open Error'
        request = self.build_request(user=self.mock_user)
        mock_ticket = Mock(spec_set=Ticket)
        mock_ticket.open.side_effect = ValueError(fake_open_error)
        mock_get.return_value = mock_ticket
        view = self.build_view(request)
        url = view.get_redirect_url(pk=fake_ticket_pk)
        self.assertEqual(url, '/admin/helpdesk/ticket/')
        mock_ticket.open.assert_called_once_with(self.mock_user)
        mock_messages.error.assert_called_once_with(
            request, 'An error occurs. {}'.format(fake_open_error))

    @patch('helpdesk.views.messages', autospec=True)
    @patch('helpdesk.views.Ticket.objects.get')
    def test_get_redirect_url_return_correct_url(self, mock_get,
                                                 mock_messages):
        """
        Test that get_get_redirect return admin ticket changelist url
        and messages.error is called with proper message.
        """
        fake_ticket_pk = 1
        request = self.build_request(user=self.mock_user)
        mock_ticket = Mock(spec_set=Ticket)
        mock_get.return_value = mock_ticket
        view = self.build_view(request)
        url = view.get_redirect_url(pk=fake_ticket_pk)
        self.assertEqual(url,
                         '/admin/helpdesk/ticket/{}/'.format(fake_ticket_pk))
        mock_ticket.open.assert_called_once_with(self.mock_user)
        mock_messages.success.assert_called_once_with(
            request,
            'Ticket n.{} is opened and assigned.'.format(fake_ticket_pk))