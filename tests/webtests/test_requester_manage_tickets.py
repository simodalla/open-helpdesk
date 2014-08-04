# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse

from django_webtest import WebTest

from openhelpdesk.models import Ticket, PRIORITY_NORMAL

from ..conftest import get_tipologies, requester, new_ticket, operator


class AddFormData(object):
    def __init__(self, content="Foo", tipologies=None, priority=None):
        self.content = content
        self.priority = priority or PRIORITY_NORMAL
        self.tipologies = [t.pk for t in tipologies] if tipologies else []


class TestAddingTicketByRequester(WebTest):

    def setUp(self):
        self.user = requester()
        self.url = reverse(admin_urlname(Ticket._meta, 'add'))
        self.content = "Foo"
        self.tipologies = get_tipologies(2)
        self.add_form_data = AddFormData(self.content, self.tipologies)

    def test_requester_field_is_setted_with_current_logged_user(self):
        response = self.app.get(self.url, user=self.user)
        form = response.forms['ticket_form']
        form['content'] = self.add_form_data.content
        form['priority'] = self.add_form_data.priority
        form['tipologies'] = self.add_form_data.tipologies
        form.submit('_save').follow()
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.requester_id, self.user.pk)
        self.assertEqual(ticket.priority, PRIORITY_NORMAL)
        self.assertIn('Foo', ticket.content)
        self.assertSetEqual(
            set(ticket.tipologies.values_list('pk', flat=True)),
            set(self.add_form_data.tipologies))

    def test_statuschangelog_obj_is_created(self):
        response = self.app.get(self.url, user=self.user)
        form = response.forms['ticket_form']
        form['content'] = self.add_form_data.content
        form['priority'] = self.add_form_data.priority
        form['tipologies'] = self.add_form_data.tipologies
        form.submit('_save')
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.status_changelogs.count(), 1)
        statuschangelog = ticket.status_changelogs.all()[0]
        self.assertEqual(statuschangelog.before, '')
        self.assertEqual(statuschangelog.after, Ticket.STATUS.new)
        self.assertEqual(statuschangelog.changer_id, self.user.pk)


class TestManageMessagesOfTicket(WebTest):

    def setUp(self):
        self.user = requester()

    def test_add_message_to_new_ticket(self):
        ticket = new_ticket(self.user, get_tipologies(2), 'Foo')
        message_content = 'help'
        recipient = operator()
        url = reverse(admin_urlname(Ticket._meta, 'change'), args=(ticket.pk,))
        response = self.app.get(url, user=self.user)
        form = response.forms['ticket_form']
        form['messages-0-content'] = message_content
        form['messages-0-recipient'].select(text=recipient.username)
        form.submit('_continue').follow()
        message = ticket.messages.latest()
        self.assertEqual(message.content, message_content)
        self.assertEqual(message.sender_id, self.user.pk)
        self.assertEqual(message.recipient_id, recipient.pk)
        response = self.app.get(url + '#tab_messages')
        message_div = response.lxml.get_element_by_id(
                        'ticket_message_{}'.format(message.pk))
        self.assertIn(message_content, message_div.text_content())






