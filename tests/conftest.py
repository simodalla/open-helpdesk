# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest


@pytest.fixture()
def rf_with_helpdeskuser(request, rf):
    rf.user = None

    class HelpdeskUser(object):
        def is_requester(self):
            return False

        def is_operator(self):
            return False

        def is_admin(self):
            return False

    rf.user = HelpdeskUser()
    return rf


def _get_tipologies(n_tipologies):
    from django.contrib.sites.models import Site
    from .factories import CategoryFactory, TipologyFactory
    from .settings_base import SITE_ID
    category = CategoryFactory()
    site = Site.objects.get(pk=SITE_ID)
    return [
        TipologyFactory(sites=(site,), category=category)
        for i in range(0, n_tipologies)]


@pytest.fixture
def tipologies():
    return _get_tipologies(2)


@pytest.fixture(scope='class')
def tipologies_cls(request):
    setattr(request.cls, 'tipologies', _get_tipologies(5))


@pytest.fixture
def ticket_content():
    return ("foo " * 20).rstrip()


@pytest.fixture
def new_ticket(requester, tipologies, ticket_content):
    """Return a ticket into 'new' status."""
    from helpdesk.models import Ticket
    ticket = Ticket.objects.create(requester=requester,
                                   content=ticket_content)
    ticket.tipologies.add(*tipologies)
    return ticket


@pytest.fixture
def initialized_ticket(new_ticket):
    new_ticket.initialize()
    return new_ticket

