# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.contrib.admin.templatetags.admin_urls import admin_urlname

from openhelpdesk.models import Ticket, PRIORITY_NORMAL


@pytest.mark.livetest
def test_add_ticket(browser_r, tipologies, ticket_content):
    browser_r.get(admin_urlname(Ticket._meta, 'add'))
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
    browser_r.driver.find_element_by_css_selector("div.result-list")
    ticket = Ticket.objects.latest()
    assert ticket.requester.pk == browser_r.user.pk
    assert ticket.priority == PRIORITY_NORMAL
    assert ticket_content in ticket.content
    assert (set(ticket.tipologies.values_list('pk', flat=True))
            == set(tipologies_pks))
