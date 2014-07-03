# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from helpdesk.models import Ticket


pytestmark = pytest.mark.django_db


@pytest.fixture
def browser_o(browser, operator):
    print('authenticated...', operator)
    browser.create_pre_authenticated_session(operator)
    return browser

@pytest.fixture
def new_tickets(requester, tipologies):
    tickets = []
    for i in range(0, 2):
        t = Ticket()
        t.requester = requester
        t.status = Ticket.STATUS.new
        t.content = 'foo '*20
        t.save()
        t.tipologies.add(*tipologies)
        tickets.append(t)
    return tickets


@pytest.mark.livetest
def test_open_more_tickets_from_action_without_error(browser_o, new_tickets):
    browser_o.get('admin:helpdesk_ticket_changelist')
    new_ticket_ids = [str(t.id) for t in new_tickets]
    for checkbox in [e for e in browser_o.driver.find_elements_by_name(
            "_selected_action")]:
        if checkbox.get_attribute('value') in new_ticket_ids:
            checkbox.click()
    browser_o.driver.find_element_by_css_selector(
        '.changelist-actions .chzn-single').click()
    for action in browser_o.driver.find_elements_by_css_selector(
            '.chzn-results li'):
        if action.text.strip().lower() == 'open e assign selected tickets':
            action.click()
    success_message = browser_o.get_messages(level='success')
    assert len(success_message) == 1
    for ticket in Ticket.objects.filter(id__in=new_ticket_ids):
        assert ticket.status == Ticket.STATUS.open
        assert ticket.assignee.id == browser_o.user.id
        assert str(ticket.id) in success_message[0].text


@pytest.mark.livetest
def test_open_more_tickets_from_action_with_errors(browser_o, new_tickets):
    new_ticket_ids = [str(t.id) for t in new_tickets]
    browser_o.get('admin:helpdesk_ticket_changelist')
    for checkbox in [e for e in browser_o.driver.find_elements_by_name(
            "_selected_action")]:
        if checkbox.get_attribute('value') in new_ticket_ids:
            checkbox.click()
    browser_o.driver.find_element_by_css_selector(
        '.changelist-actions .chzn-single').click()
    exc = Exception('Error')
    for action in browser_o.driver.find_elements_by_css_selector(
            '.chzn-results li'):
        if action.text.strip().lower() == 'open e assign selected tickets':
            with patch('helpdesk.models.Ticket.opening', side_effect=exc):
                action.click()
    error_message = browser_o.get_messages(level='error')
    assert len(error_message) == 1
    for ticket in Ticket.objects.filter(id__in=new_ticket_ids):
        assert ticket.status == Ticket.STATUS.new
        assert ticket.assignee is None
        assert str(ticket.id) in error_message[0].text
        assert 'Error' in error_message[0].text


@pytest.mark.target
@pytest.mark.livetest
def test_add_report_to(browser_o, new_tickets):
    new_ticket_ids = [str(t.id) for t in new_tickets]
    browser_o.get('admin:helpdesk_ticket_changelist')
    for checkbox in [e for e in browser_o.driver.find_elements_by_name(
            "_selected_action")]:
        if checkbox.get_attribute('value') in new_ticket_ids:
            checkbox.click()
    browser_o.driver.find_element_by_css_selector(
        '.changelist-actions .chzn-single').click()
    exc = Exception('Error')
    for action in browser_o.driver.find_elements_by_css_selector(
            '.chzn-results li'):
        if action.text.strip().lower() == 'open e assign selected tickets':
            with patch('helpdesk.models.Ticket.opening', side_effect=exc):
                action.click()
    error_message = browser_o.get_messages(level='error')
    assert len(error_message) == 1
    for ticket in Ticket.objects.filter(id__in=new_ticket_ids):
        assert ticket.status == Ticket.STATUS.new
        assert ticket.assignee is None
        assert str(ticket.id) in error_message[0].text
        assert 'Error' in error_message[0].text

