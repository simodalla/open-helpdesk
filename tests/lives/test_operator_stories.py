# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils import timezone

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from openhelpdesk.models import Ticket, StatusChangesLog, Report


@pytest.fixture
def browser_o(browser, operator):
    browser.create_pre_authenticated_session(operator)
    return browser


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
def test_add_report_to_open_ticket_with_put_on_pending_action(
        browser_o, opened_ticket):
    content = 'foo ' * 10
    action = 'put_on_pending'
    days_after_today = 4
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
    datepicker = WebDriverWait(browser_o.driver, 10).until(
        ec.visibility_of_element_located(
            (By.CSS_SELECTOR, 'table.ui-datepicker-calendar')))
    datepicker.find_element_by_link_text(
        str((now + timezone.timedelta(days=days_after_today)).day)).click()
    browser_o.driver.find_element_by_name('_save').click()
    browser_o.driver.find_element_by_id("ticket_form")
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
