# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from helpdesk.models import Ticket, Tipology, PRIORITY_NORMAL


@pytest.mark.usefixtures('requester_cls', 'tipologies_cls')
class TestRequesterAddTicket(WebTest):

    def setUp(self):
        self.ticket_content = ("foo " * 20).rstrip()

    @pytest.mark.usefixtures('ticket_content')
    def test_adding_ticket_set_requester_field(self):
        """
        Test that adding new ticket, the field requester is setted with
        logged user.
        """
        index = self.app.get(
            reverse(admin_urlname(Ticket._meta, 'add')), user=self.requester)
        form = index.forms['ticket_form']
        form['content'] = self.ticket_content
        form['priority'] = PRIORITY_NORMAL
        tipologies_selected = [t for t in self.tipologies[0:2]]
        form['tipologies'] = tipologies_selected
        response = form.submit('_save').follow()
        response.lxml.cssselect('.result-list')
        ticket = Ticket.objects.latest()
        assert ticket.requester.pk == self.requester.pk
        assert ticket.priority == PRIORITY_NORMAL
        assert self.ticket_content in ticket.content
        assert (set(ticket.tipologies.values_list('pk', flat=True))
                == set(tipologies_selected))