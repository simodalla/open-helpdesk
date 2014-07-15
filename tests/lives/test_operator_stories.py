# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from helpdesk.models import Ticket, StatusChangesLog, Report


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
        t.content = 'foo ' * 20
        t.save()
        t.tipologies.add(*tipologies)
        t.initialize()
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


@pytest.mark.livetest
def test_open_ticket_from_change_view(browser_o, initialized_ticket):
    change_url = reverse(admin_urlname(Ticket._meta, 'change'),
                         args=(initialized_ticket.id,))
    browser_o.get(change_url)
    open_link = WebDriverWait(browser_o.driver, 10).until(
        ec.presence_of_element_located((By.LINK_TEXT, 'Open and assign to me'))
    )
    open_link.click()
    messages = browser_o.get_messages('success')
    assert len(messages) == 1
    WebDriverWait(browser_o.driver, 10).until(
        ec.visibility_of_element_located((By.ID, 'tab_changestatuslog'))
    )
    WebDriverWait(browser_o.driver, 10).until(
        ec.invisibility_of_element_located((By.ID, 'tab_messages'))
    )
    status_changelogs = StatusChangesLog.objects.filter(
        ticket=initialized_ticket)
    initialized_ticket = Ticket.objects.get(id=initialized_ticket.id)
    assert status_changelogs.count() == 2
    assert initialized_ticket.status == Ticket.STATUS.open
    browser_o.driver.find_elements_by_id(
        'ticket_statuschangelog_{}'.format(initialized_ticket.pk))


@pytest.mark.livetest
def test_add_report_to_open_ticket_without_action(browser_o, opened_ticket):
    content = 'foo ' * 10
    action = 'no_action'
    browser_o.get('admin:helpdesk_ticket_change', *(opened_ticket.id,))
    browser_o.driver.find_element_by_id('add_report_to_ticket').click()
    browser_o.driver.find_element_by_id('id_content').send_keys(content)
    visible_from_req = browser_o.driver.find_element_by_id(
        'id_visible_from_requester')
    if visible_from_req.is_selected():
        visible_from_req.click()
    browser_o.driver.find_element_by_css_selector(
        'input[value="{}"]'.format(action)).click()
    browser_o.driver.find_element_by_name('_save').click()
    report = Report.objects.filter(ticket__id=opened_ticket.id).latest()
    assert report.ticket.id == opened_ticket.id
    assert report.content == content
    assert report.sender.pk == browser_o.user.pk
    assert report.recipient.pk == opened_ticket.requester.pk
    assert report.action_on_ticket == action
    assert report.visible_from_requester is False
    WebDriverWait(browser_o.driver, 10).until(
        ec.visibility_of_element_located((By.ID, 'ticket_form')),
        message='It seems that not redirect to ticket change form. Current'
                ' url is: {}'.format(browser_o.current_url)
    )