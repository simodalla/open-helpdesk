# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse

from helpdesk.models import Ticket, PRIORITY_NORMAL

pytestmark = pytest.mark.django_db


class TestAddTicket(object):
    def test_requester_field_is_setted_with_current_logged_user(
            self, app, requester, tipologies, ticket_content):
        response = app.get(reverse(admin_urlname(Ticket._meta, 'add')),
                           user=requester)
        form = response.forms['ticket_form']
        form['content'] = ticket_content
        form['priority'] = PRIORITY_NORMAL
        tipologies_selected = [t.pk for t in tipologies[0:2]]
        form['tipologies'] = tipologies_selected
        form.submit('_save').follow()
        ticket = Ticket.objects.latest()
        assert ticket.requester.pk == requester.pk
        assert ticket.priority == PRIORITY_NORMAL
        assert ticket.content in ticket.content
        assert (set(ticket.tipologies.values_list('pk', flat=True))
                == set(tipologies_selected))
