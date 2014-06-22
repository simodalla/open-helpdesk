# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from selenium.webdriver.support.ui import Select

from helpdesk.models import Ticket, PRIORITY_NORMAL


pytestmark = pytest.mark.django_db


@pytest.mark.livetest
def test_add_ticket(browser_r, tipologies, ticket_content):
    browser_r.get('admin:helpdesk_ticket_add')
    print(id(browser_r))
    tipologies_pks = []
    for t in tipologies:
        tipologies_pks.append(t.pk)
        browser_r.driver.find_element_by_css_selector(
            "#id_tipologies_from option[value='{}']".format(t.pk)).click()
        browser_r.driver.find_element_by_css_selector(
            '#id_tipologies_add_link').click()
    browser_r.set_content_to_tinymce(ticket_content)
    # select priority to PRIORITY_NORMAL
    browser_r.driver.find_element_by_css_selector(
        "#id_priority input[value='{}']".format(PRIORITY_NORMAL)).click()
    browser_r.driver.find_element_by_name('_save').click()
    ticket = Ticket.objects.latest()
    assert ticket.requester.pk == browser_r.user.pk
    assert ticket.priority == PRIORITY_NORMAL
    assert ticket_content in ticket.content
    assert (set(ticket.tipologies.values_list('pk', flat=True))
            == set(tipologies_pks))


@pytest.mark.target
@pytest.mark.livetest
def test_add_message_to_new_ticket(browser_r, new_ticket, operator, settings):
    assert isinstance(new_ticket, Ticket)
    message_content = 'help'
    # requester got to 'change' view
    browser_r.get('admin:helpdesk_ticket_change', new_ticket.pk)
    # requester insert message's content
    browser_r.driver.find_element_by_id(
        'id_messages-0-content').send_keys(message_content)
    # requester select an user recipient
    select = Select(browser_r.driver.find_element_by_id(
        'id_messages-0-recipient'))
    select.select_by_visible_text(operator.username)
    # requester click on Save button
    browser_r.driver.find_element_by_name('_continue').click()
    try:
        message = new_ticket.messages.all()[0]
    except IndexError:
        pytest.fail("Message objects related to ticket isn't create.")
    assert message.content == message_content
    assert message.sender.pk == browser_r.user.pk
    assert message.recipient.pk == operator.pk
    fieldset_messages = browser_r.driver.find_element_by_id('ticket_messages')
    assert len(fieldset_messages.find_elements_by_css_selector(
        'div.form-row')) == 1
    ticket_message = fieldset_messages.find_element_by_id(
        'ticket_message_{}'.format(message.id))
    assert message.content in ticket_message.text
