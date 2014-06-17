# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.contrib.sites.models import Site

from helpdesk.models import Ticket, PRIORITY_NORMAL

from ..factories import CategoryFactory, TipologyFactory
from ..settings import SITE_ID


pytestmark = pytest.mark.django_db


@pytest.fixture(scope='module')
def tipologies():
    category = CategoryFactory()
    site = Site.objects.get(pk=SITE_ID)
    tipologies = [
        TipologyFactory(sites=(site,), category=category).pk
        for i in range(0, 2)]
    return tipologies


@pytest.fixture(scope='module')
def ticket_content(scope='module'):
    return ("foo " * 20).rstrip()


def test_add_booking_type(browser_requestered, tipologies, ticket_content):
    print(tipologies, ticket_content)
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
