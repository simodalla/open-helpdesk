# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from helpdesk.models import Ticket, PRIORITY_NORMAL


pytestmark = pytest.mark.django_db


def test_add_booking_type(browser_requestered, tipologies, ticket_content):
    browser, requester = browser_requestered
    browser.get('admin:helpdesk_ticket_add')
    for t in tipologies:
        browser.driver.find_element_by_css_selector(
            "#id_tipologies_from option[value='{}']".format(t)).click()
        browser.driver.find_element_by_css_selector(
            '#id_tipologies_add_link').click()
    browser.set_content_to_tinymce(ticket_content)
    # select priority to PRIORITY_NORMAL
    browser.driver.find_element_by_css_selector(
        "#id_priority input[value='{}']".format(PRIORITY_NORMAL)).click()
    browser.driver.find_element_by_name('_save').click()
    ticket = Ticket.objects.latest()
    assert ticket.requester.pk == requester.pk
    assert ticket.priority == PRIORITY_NORMAL
    assert ticket_content in ticket.content
    assert (set(ticket.tipologies.values_list('pk', flat=True))
            == set(tipologies))
