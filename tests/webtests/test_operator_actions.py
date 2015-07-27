# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib import messages
from django.core.urlresolvers import reverse

from openhelpdesk.models import Report, Ticket

pytestmark = pytest.mark.django_db


@pytest.fixture
def new_tickets(requester, tipologies):
    tickets = []
    for i in range(0, 2):
        t = Ticket()
        t.requester = requester
        t.status = Ticket.STATUS.new
        t.content = 'foo ' * 20
        t.save()
        t.tipologies.add(*tipologies)
        t.initialize()
        tickets.append(t)
    return tickets


def get_add_report_url(ticket):
    return '{}?ticket={}'.format(reverse(admin_urlname(Report._meta, 'add')),
                                 ticket.pk)


def test_open_more_tickets_from_action_without_error(app, operator,
                                                     new_tickets):
    new_ticket_ids = [t.pk for t in new_tickets]
    response = app.get(reverse(admin_urlname(Ticket._meta, 'changelist')),
                       user=operator)
    form = response.forms[0]
    form['_selected_action'] = new_ticket_ids
    form['action'].select(text='Open e assign selected Tickets')
    response = form.submit().follow()
    assert 'messages' in response.context
    request_messages = [m for m in response.context['messages']]
    assert len(request_messages) == 1
    assert request_messages[0].level == messages.SUCCESS
    for ticket in Ticket.objects.filter(id__in=new_ticket_ids):
        assert ticket.status == Ticket.STATUS.open
        assert ticket.assignee_id == operator.pk
        assert str(ticket.id) in request_messages[0].message


def test_open_more_tickets_from_action_with_errors(app, operator, new_tickets):
    new_ticket_ids = [t.pk for t in new_tickets]
    response = app.get(reverse(admin_urlname(Ticket._meta, 'changelist')),
                       user=operator)
    form = response.forms[0]
    form['_selected_action'] = new_ticket_ids
    form['action'].select(text='Open e assign selected Tickets')
    exc = Exception('Error')
    with patch('openhelpdesk.models.Ticket.opening', side_effect=exc):
        response = form.submit().follow()

    assert 'messages' in response.context
    request_messages = [m for m in response.context['messages']]
    assert len(request_messages) == 1
    assert request_messages[0].level == messages.ERROR
    for ticket in Ticket.objects.filter(id__in=new_ticket_ids):
        assert ticket.status == Ticket.STATUS.new
        assert ticket.assignee_id is None
        assert str(ticket.id) in request_messages[0].message
        assert 'Error' in request_messages[0].message


def test_add_report_to_open_ticket_without_action(app, opened_ticket):
    assert Report.objects.count() == 0
    pre_changelogs = opened_ticket.status_changelogs.count()
    response = app.get(get_add_report_url(opened_ticket),
                       user=opened_ticket.assignee)
    action = 'no_action'

    form = response.forms['_form']
    form['content'] = 'foo'
    form['visible_from_requester'] = False
    form['action_on_ticket'] = action
    form.submit('_save')
    report = Report.objects.filter(ticket=opened_ticket).latest()
    assert report.content == 'foo'
    assert report.action_on_ticket == action
    assert report.visible_from_requester is False
    assert report.sender.pk == opened_ticket.assignee.pk
    assert report.recipient.pk == opened_ticket.requester.pk
    assert report.ticket.status == Ticket.STATUS.open
    assert report.ticket.status_changelogs.count() == pre_changelogs


def test_add_report_to_open_ticket_with_close_action(app, opened_ticket):
    assert Report.objects.count() == 0
    pre_changelogs = opened_ticket.status_changelogs.count()
    response = app.get(get_add_report_url(opened_ticket),
                       user=opened_ticket.assignee)
    action = 'close'
    form = response.forms['_form']
    form['content'] = 'foo'
    form['visible_from_requester'] = False
    form['action_on_ticket'] = action
    form.submit('_save')
    report = Report.objects.filter(ticket=opened_ticket).latest()
    assert report.content == 'foo'
    assert report.action_on_ticket == action
    assert report.visible_from_requester is False
    assert report.sender.pk == opened_ticket.assignee.pk
    assert report.recipient.pk == opened_ticket.requester.pk
    assert report.ticket.status == Ticket.STATUS.closed
    assert report.ticket.status_changelogs.count() == pre_changelogs + 1
    statuschangelog = report.ticket.status_changelogs.latest()
    assert statuschangelog.before == Ticket.STATUS.open
    assert statuschangelog.after == Ticket.STATUS.closed
    assert statuschangelog.changer_id == opened_ticket.assignee.pk


def test_add_report_to_peding_ticket_without_action(app, pending_ticket):
    assert Report.objects.count() == 0
    pre_changelogs = pending_ticket.status_changelogs.count()
    response = app.get(get_add_report_url(pending_ticket),
                       user=pending_ticket.assignee)
    action = 'no_action'
    form = response.forms['_form']
    form['content'] = 'foo'
    form['visible_from_requester'] = True
    form['action_on_ticket'] = action
    form.submit('_save')
    report = Report.objects.filter(ticket=pending_ticket).latest()
    assert report.content == 'foo'
    assert report.action_on_ticket == action
    assert report.visible_from_requester is True
    assert report.sender.pk == pending_ticket.assignee.pk
    assert report.recipient.pk == pending_ticket.requester.pk
    assert report.ticket.status == Ticket.STATUS.pending
    assert report.ticket.status_changelogs.count() == pre_changelogs
