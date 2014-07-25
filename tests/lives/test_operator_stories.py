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


@pytest.mark.livetest
def test_add_report_to_open_ticket_with_close_action(browser_o, opened_ticket):
    content = 'foo ' * 10
    action = 'close'
    browser_o.get(reverse(admin_urlname(Report._meta, 'add')) +
                  '?ticket={}'.format(opened_ticket.id,))
    browser_o.driver.find_element_by_id('id_content').send_keys(content)
    visible_from_req = browser_o.driver.find_element_by_id(
        'id_visible_from_requester')
    if visible_from_req.is_selected():
        visible_from_req.click()
    browser_o.driver.find_element_by_css_selector(
        'input[value="{}"]'.format(action)).click()
    browser_o.driver.find_element_by_name('_save').click()
    # pytest.set_trace()
    report = Report.objects.filter(ticket__id=opened_ticket.id).latest()
    assert report.ticket.id == opened_ticket.id
    assert report.content == content
    assert report.sender.pk == browser_o.user.pk
    assert report.recipient.pk == opened_ticket.requester.pk
    assert report.action_on_ticket == action
    assert report.visible_from_requester is False
    ticket = Ticket.objects.get(id=opened_ticket.id)
    assert ticket.status == Ticket.STATUS.closed
    statuschangelog = ticket.status_changelogs.latest()
    assert statuschangelog.before == Ticket.STATUS.open
    assert statuschangelog.after == Ticket.STATUS.closed
    assert statuschangelog.changer.pk == browser_o.user.pk
    WebDriverWait(browser_o.driver, 10).until(
        ec.visibility_of_element_located((By.ID, 'ticket_form')),
        message='It seems that not redirect to ticket change form. Current'
                ' url is: {}'.format(browser_o.current_url)
    )

@pytest.mark.livetest
def test_add_report_to_open_ticket_with_put_on_pending_action(
        browser_o, opened_ticket):
    content = 'foo ' * 10
    action = 'put_on_pending'
    days_after_today = 2
    from django.utils import timezone
    now = timezone.now()
    browser_o.get(reverse(admin_urlname(Report._meta, 'add')) +
                  '?ticket={}'.format(opened_ticket.id,))
    browser_o.driver.find_element_by_id('id_content').send_keys(content)
    visible_from_req = browser_o.driver.find_element_by_id(
        'id_visible_from_requester')
    if visible_from_req.is_selected():
        visible_from_req.click()
    browser_o.driver.find_element_by_css_selector(
        'input[value="{}"]'.format(action)).click()
    estimated_end_pending_date = WebDriverWait(browser_o.driver, 10).until(
        ec.visibility_of_element_located(
            (By.ID, 'id_estimated_end_pending_date')))
    estimated_end_pending_date.click()
    WebDriverWait(browser_o.driver, 10).until(
        ec.visibility_of_element_located(
            (By.CSS_SELECTOR, 'td.ui-datepicker-today{}'.format(
                ' + td' * days_after_today)))).click()
    browser_o.driver.find_element_by_name('_save').click()
    report = Report.objects.filter(ticket__id=opened_ticket.id).latest()
    assert report.ticket.id == opened_ticket.id
    assert report.content == content
    assert report.sender.pk == browser_o.user.pk
    assert report.recipient.pk == opened_ticket.requester.pk
    assert report.action_on_ticket == action
    assert report.visible_from_requester is False
    ticket = Ticket.objects.get(id=opened_ticket.id)
    assert ticket.status == Ticket.STATUS.pending
    statuschangelog = ticket.status_changelogs.latest()
    assert statuschangelog.before == Ticket.STATUS.open
    assert statuschangelog.after == Ticket.STATUS.pending
    assert statuschangelog.changer.pk == browser_o.user.pk
    pending_range = ticket.pending_ranges.all().latest()
    expected_estimated_end_date = now + timezone.timedelta(
        days=days_after_today)
    assert pending_range.estimated_end.year == expected_estimated_end_date.year
    assert (pending_range.estimated_end.month ==
            expected_estimated_end_date.month)
    assert pending_range.estimated_end.day == expected_estimated_end_date.day
    assert pending_range.start == statuschangelog.created


@pytest.mark.livetest
def test_add_report_for_remove_from_from_pending_the_ticket(
        browser_o, pending_ticket):
    """
    :param browser_o:
    :type browser_o: tests.lives.MezzanineLiveBrowser
    :param pending_ticket:
    :type pending_ticket: helpdesk.models.Ticket
    """
    content = 'foo ' * 10
    action = 'remove_from_pending'
    browser_o.get(reverse(admin_urlname(Report._meta, 'add')) +
                  '?ticket={}'.format(pending_ticket.pk,))
    # insert the content of report
    browser_o.driver.find_element_by_id('id_content').send_keys(content)
    visible_from_req = browser_o.driver.find_element_by_id(
        'id_visible_from_requester')
    # select the checkbox for requester's visibility
    if not visible_from_req.is_selected():
        visible_from_req.click()
    # select the action 'remove_from_pending'
    browser_o.driver.find_element_by_css_selector(
        'input[value="{}"]'.format(action)).click()
    # select save button
    browser_o.driver.find_element_by_name('_save').click()
    browser_o.get(reverse(admin_urlname(Ticket._meta, 'change'),
                          args=(pending_ticket.id,)))
    tab_ticket_data = WebDriverWait(browser_o.driver, 10).until(
        ec.visibility_of_element_located((By.ID, 'tab_ticket_data')))
    status = tab_ticket_data.find_element_by_css_selector(
        ".table_ticket_data td.ticket_status")
    assert status.text.strip().lower() == 'open'
    # select tab of Messages
    browser_o.driver.find_element_by_css_selector(
        'a[href="#tab_messages"]').click()
    report = Report.objects.filter(ticket_id=pending_ticket.id).latest()
    message = browser_o.driver.find_element_by_id(
        'ticket_message_{}'.format(report.id))
    assert content in message.text
