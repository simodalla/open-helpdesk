# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from future.builtins import str

import six

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.sites.models import Site
from django.core import mail
from django.core.urlresolvers import reverse

from mezzanine.utils.sites import current_site_id

from django_webtest import WebTest

from openhelpdesk.models import Ticket, PRIORITY_NORMAL, SiteConfiguration

from ..conftest import get_tipologies, requester, new_ticket, operator


class AddFormData(object):
    def __init__(self, content="Foo", tipologies=None, priority=None):
        self.content = content
        self.priority = priority or PRIORITY_NORMAL
        self.tipologies = [str(t.pk) for t in tipologies] if tipologies else []


class TestAddingTicket(WebTest):

    def setUp(self):
        self.user = requester()
        self.url = reverse(admin_urlname(Ticket._meta, 'add'))
        self.content = "Foo"
        self.tipologies = get_tipologies(2)
        self.add_form_data = AddFormData(self.content, self.tipologies)
        response = self.app.get(self.url, user=self.user)
        # support django 1.8 and previus version
        form_id = '_form' if '_form' in response.forms else 'ticket_form'
        # import ipdb
        # ipdb.set_trace()
        self.form = response.forms[form_id]
        self.form['content'] = self.add_form_data.content
        self.form['priority'] = self.add_form_data.priority
        import pytest
        pytest.set_trace()
        # print(self.add_form_data.tipologies)
        self.form['tipologies'] = self.add_form_data.tipologies

    def test_requester_field_is_setted_with_current_logged_user(self):
        self.form.submit('_save').follow()
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.requester_id, self.user.pk)
        self.assertEqual(ticket.priority, PRIORITY_NORMAL)
        self.assertIn('Foo', ticket.content)
        self.assertSetEqual(
            set(ticket.tipologies.values_list('pk', flat=True)),
            set(self.add_form_data.tipologies))

    def test_statuschangelog_obj_is_created(self):
        self.form.submit('_save')
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.status_changelogs.count(), 1)
        statuschangelog = ticket.status_changelogs.all()[0]
        self.assertEqual(statuschangelog.before, '')
        self.assertEqual(statuschangelog.after, Ticket.STATUS.new)
        self.assertEqual(statuschangelog.changer_id, self.user.pk)

    def test_email_is_sent_to_operators(self):
        site_conf = SiteConfiguration(
            site=Site.objects.get(pk=current_site_id()))
        site_conf._email_addr_from = 'helpdesk@example.com'
        site_conf._email_addr_to_1 = 'support@example.com'
        site_conf.save()
        self.form.submit('_save')
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        """:type : django.core.mail.EmailMessage"""
        self.assertEqual(email.subject,
                         "New ticket created by {}".format(self.user.username))
        self.assertSetEqual(set(email.to), set(site_conf.email_addrs_to))
        self.assertEqual(email.from_email, site_conf.email_addr_from)


class TestManageMessagesOfTicket(WebTest):

    def setUp(self):
        self.user = requester()

    def test_add_message_to_new_ticket(self):
        ticket = new_ticket(self.user, get_tipologies(2), 'Foo')
        message_content = 'help'
        url = reverse(admin_urlname(Ticket._meta, 'change'), args=(ticket.pk,))
        response = self.app.get(url, user=self.user)
        # support django 1.8 and previus version
        form_id = '_form' if '_form' in response.forms else 'ticket_form'
        form = response.forms[form_id]
        form['messages-0-content'] = message_content
        form.submit('_continue').follow()
        message = ticket.messages.latest()
        self.assertEqual(message.content, message_content)
        self.assertEqual(message.sender_id, self.user.pk)
        self.assertIsNone(message.recipient)
        response = self.app.get(url + '#tab_messages')
        message_div = response.lxml.get_element_by_id(
            'ticket_message_{}'.format(message.pk))
        self.assertIn(message_content, message_div.text_content())
