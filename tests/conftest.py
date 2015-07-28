# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


@pytest.fixture(scope='module')
def stringios():
    from six.moves import cStringIO
    return cStringIO(), cStringIO()


@pytest.fixture
def app(request):
    """Fixture for use Webtest (django-webtest)"""
    from django_webtest import WebTestMixin
    wt = WebTestMixin()
    wt._patch_settings()
    request.addfinalizer(wt._unpatch_settings)
    wt.renew_app()
    return wt.app


def helpdesker(helpdesker_conf):
    import openhelpdesk.defaults
    from tests.factories import HelpdeskerF, GroupFactory
    from mezzanine.utils.sites import current_site_id

    helpdesker_conf = getattr(openhelpdesk.defaults, helpdesker_conf, None)
    if not helpdesker_conf:
        return None
    user = HelpdeskerF(
        username=helpdesker_conf[0].rstrip('s'),
        groups=[GroupFactory(name=helpdesker_conf[0],
                             permissions=list(helpdesker_conf[1]))])

    # import pdb
    # pdb.set_trace()
    if user.sitepermissions.sites.count() == 0:
        user.sitepermissions.sites.add(current_site_id())
    # site_perm, created = user.sitepermissions.get_or_create(user=user)
    return user


@pytest.fixture
def requester():
    return helpdesker('HELPDESK_REQUESTERS')


@pytest.fixture
def operator():
    return helpdesker('HELPDESK_OPERATORS')


class ModelAdminUtil(object):
    def __init__(self):
        self.rf = None
        self._user = None
        self.request = None
        self.model_admin = None
        self.obj = None
        self.form = Mock()
        self.qs = None

    def get(self, path):
        request = self.rf.get(path)
        request.user = self.user
        return request

    def post(self, path, data=None):
        request = self.rf.post(path, data)
        request.user = self.user
        return request

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, helpdeskuser):
        for type_helpdeskuser in ['requester', 'operator', 'admin']:
            mock = getattr(self._user, 'is_{}'.format(type_helpdeskuser))
            mock.return_value = (
                True if helpdeskuser == type_helpdeskuser else False)


@pytest.fixture
def model_admin_util(rf):
    from openhelpdesk.core import HelpdeskUser
    from django.db.models.query import QuerySet

    mau = ModelAdminUtil()
    mau.rf = rf
    mau._user = Mock(spec_set=HelpdeskUser, name='helpdeskuser',
                     is_operator=Mock(return_value=False),
                     is_requester=Mock(return_value=False),
                     is_admin=Mock(return_value=False))
    mau.qs = Mock(spec_set=QuerySet, name='queryset')
    mau.request = mau.get('/admin/fake/')

    return mau


@pytest.fixture
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


def get_tipologies(n_tipologies):
    from django.contrib.sites.models import Site
    from .factories import CategoryFactory, TipologyFactory
    from mezzanine.utils.sites import current_site_id
    category = CategoryFactory()
    site = Site.objects.get(pk=current_site_id())
    return [
        TipologyFactory(sites=(site,), category=category)
        for i in range(0, n_tipologies)]


@pytest.fixture
def tipologies():
    return get_tipologies(2)


@pytest.fixture
def ticket_content():
    return ("foo " * 20).rstrip()


@pytest.fixture
def new_ticket(requester, tipologies, ticket_content):
    """Return a ticket into 'new' status."""
    from openhelpdesk.models import Ticket
    ticket = Ticket.objects.create(requester=requester,
                                   content=ticket_content)
    ticket.tipologies.add(*tipologies)
    return ticket


@pytest.fixture
def initialized_ticket(new_ticket):
    new_ticket.initialize()
    return new_ticket


@pytest.fixture
def opened_ticket(initialized_ticket, operator):
    initialized_ticket.opening(operator)
    return initialized_ticket


@pytest.fixture
def pending_ticket(opened_ticket, operator):
    import datetime
    from django.utils import timezone
    estimated_end_date = (
        timezone.now() + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
    opened_ticket.put_on_pending(operator,
                                 estimated_end_date=estimated_end_date)
    return opened_ticket
