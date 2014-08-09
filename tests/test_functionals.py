# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django import VERSION as DJANGO_VERSION
from django.contrib.sites.models import Site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.test import TestCase
from lxml.html import fromstring

from openhelpdesk.defaults import (HELPDESK_REQUESTERS,
                                   HELPDESK_MAX_TIPOLOGIES_FOR_TICKET)
from openhelpdesk.models import Ticket, Tipology, Category, Report
from openhelpdesk.admin import MessageInline
from .helpers import AdminTestMixin
from .factories import (
    UserFactory, CategoryFactory, GroupFactory, SiteFactory, TicketFactory,
    TipologyFactory)


class RequesterMakeTicketTest(AdminTestMixin, TestCase):
    def setUp(self):
        self.requester = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        self.client.login(username=self.requester.username, password='default')
        self.post_data = self.get_formset_post_data(
            data={'content': 'helpdesk_content', 'tipologies': None,
                  'priority': 1},
            formset='openhelpdesk-attachment-content_type-object_id')
        self.default_site = Site.objects.get(pk=1)

    def get_category(self, n_tipologies=None, site=None):
        if not n_tipologies:
            n_tipologies = HELPDESK_MAX_TIPOLOGIES_FOR_TICKET
        tipology_names = ['tip{}'.format(i) for i in range(0, n_tipologies)]
        category = CategoryFactory(tipologies=tipology_names)
        if site is None:
            site = self.default_site
        [t.sites.add(site) for t in category.tipologies.all()]
        self.post_data.update({'tipologies': category.tipology_pks})
        return category

    def test_adding_ticket_set_requester_field(self):
        """
        Test that adding new ticket, the field requester is setted with
        logged user.
        """
        self.get_category(2)
        self.client.post(self.get_url(Ticket, 'add'), data=self.post_data)
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.requester.pk, self.requester.pk)

    def test_changelist_view_is_filtered(self):
        """
        Test that the changelist is filtered by tickets with requester's field
        matching to logged user.
        """
        n = 2
        category = self.get_category(1)
        for user in [self.requester, UserFactory(
                groups=self.requester.groups.all())]:
            [TicketFactory(requester=user,
                           tipologies=category.tipologies.all())
             for i in range(0, n)]
        response = self.client.get(self.get_url(Ticket, 'changelist'))
        if DJANGO_VERSION < (1, 6):
            tickets_pks = response.context['cl'].result_list.values_list(
                'pk', flat=True)
        else:
            tickets_pks = response.context['cl'].queryset.values_list(
                'pk', flat=True)
        self.assertEqual(len(tickets_pks), n)
        self.assertEqual(
            set(tickets_pks),
            set(self.requester.requested_tickets.values_list('pk', flat=True)))

    def test_form_with_less_tipologies_fields_is_validate(self):
        self.get_category(HELPDESK_MAX_TIPOLOGIES_FOR_TICKET - 1)
        assert (len(self.post_data['tipologies'])
                < HELPDESK_MAX_TIPOLOGIES_FOR_TICKET)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertRedirects(response, self.get_url(Ticket, 'changelist'))

    def test_form_with_equals_tipologies_fields_is_validate(self):
        self.get_category(HELPDESK_MAX_TIPOLOGIES_FOR_TICKET)
        assert (len(self.post_data['tipologies'])
                == HELPDESK_MAX_TIPOLOGIES_FOR_TICKET)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertRedirects(response, self.get_url(Ticket, 'changelist'))

    def test_form_with_more_tipologies_fields_is_not_validate(self):
        self.get_category(HELPDESK_MAX_TIPOLOGIES_FOR_TICKET + 1)
        assert (len(self.post_data['tipologies'])
                > HELPDESK_MAX_TIPOLOGIES_FOR_TICKET)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertEqual(response.status_code, 200)
        self.assertAdminFormError(response, 'tipologies',
                                  'Too many tipologies selected. You can'
                                  ' select a maximum of {}.'.format(
                                      HELPDESK_MAX_TIPOLOGIES_FOR_TICKET))

    def test_tipologies_field_is_filtered_by_current_site(self):
        category_in_site = self.get_category(2)
        category_not_in_site = self.get_category(2, site=SiteFactory.create())
        response = self.client.get(self.get_url(Ticket, 'add'))
        dom = fromstring(response.content)
        form_tipologies = {int(option.attrib['value']) for option
                           in dom.cssselect('#id_tipologies option')}
        self.assertSetEqual(form_tipologies,
                            {c.pk for c in category_in_site.tipologies.all()})
        self.assertSetEqual(
            form_tipologies.intersection(
                {c.pk for c in category_not_in_site.tipologies.all()}), set())

    def test_add_ticket_dont_have_messageinline_in_formset(self):
        """
        Test that in add ticket view, MessageInline not in formsets.
        """
        self.get_category(2)
        response = self.client.get(self.get_url(Ticket, 'add'))
        self.assertInlineClassNotInFormset(response, MessageInline)

    def test_change_ticket_have_messageinline_in_formset(self):
        """
        Test that in change ticket view, MessageInline in formsets.
        """
        category = self.get_category(1)
        ticket = TicketFactory(content='',
                               requester=self.requester,
                               tipologies=category.tipologies.all())
        response = self.client.get(
            self.get_url(Ticket, 'change', args=(ticket.pk,)))
        self.assertInlineClassInFormset(response, MessageInline)


class CategoryAndTipologyTest(AdminTestMixin, TestCase):
    def setUp(self):
        self.admin = UserFactory(is_superuser=True)
        self.client.login(username=self.admin.username,
                          password='default')
        self.tipology = TipologyFactory(
            category=CategoryFactory(),
            sites=[SiteFactory() for i in range(0, 2)])

    def test_view_site_from_tipology_changelist_view(self):
        response = self.client.get(self.get_url(Tipology, 'changelist'))
        dom = fromstring(response.content)
        view_site_links = dom.cssselect('a.view_site')
        self.assertEqual(len(view_site_links),
                         self.tipology.sites.count())
        response = self.client.get(view_site_links[0].get('href'))
        self.assertEqual(response.status_code, 200)
        dom = fromstring(response.content)
        self.assertEqual(
            len(dom.cssselect('div.result-list table tbody tr')), 1)

    def test_view_category_from_tipology_changelist_view(self):
        response = self.client.get(self.get_url(Tipology, 'changelist'))
        dom = fromstring(response.content)
        view_category_links = dom.cssselect('a.view_category')
        self.assertEqual(len(view_category_links), 1)
        response = self.client.get(view_category_links[0].get('href'))
        self.assertEqual(response.status_code, 200)
        dom = fromstring(response.content)
        self.assertEqual(
            len(dom.cssselect('div.result-list table tbody tr')), 1)

    def test_view_tipology_from_category_changelist_view(self):
        TipologyFactory(category=self.tipology.category)
        response = self.client.get(self.get_url(Category, 'changelist'))
        dom = fromstring(response.content)
        view_tipology_links = dom.cssselect('a.view_tipology')
        self.assertEqual(len(view_tipology_links), 2)
        for link in view_tipology_links:
            response = self.client.get(link.get('href'))
            self.assertEqual(response.status_code, 200)
            dom = fromstring(response.content)
            self.assertEqual(
                len(dom.cssselect('div.result-list table tbody tr')),
                1)


@pytest.mark.django_db
def test_object_tools_view(client, operator):
    print(operator)
    print(operator.groups.all())
    print(client.login(username=operator.username, password='default'))
    client.get('/admin/openhelpdesk/ticket/object_tools/'
               '?view=/admin/openhelpdesk/ticket/4/')


@pytest.fixture
def change_view(request, initialized_ticket):
    class ChangeViewUtil(object):
        def __init__(self):
            self.ticket = initialized_ticket
            self.url = reverse(admin_urlname(Ticket._meta, 'change'),
                               args=(initialized_ticket.pk,))
    return ChangeViewUtil()


@pytest.fixture
def client_r(client, requester):
    client.login(username=requester.username, password='default')
    return client


@pytest.fixture
def client_o(client, operator):
    client.login(username=operator.username, password='default')
    return client


@pytest.mark.django_db
class TestTicketChangeView(object):

    def test_custom_template_renderized(self, client_r, change_view):
        response = client_r.get(change_view.url)
        assert (response.templates[0].name ==
                'admin/openhelpdesk/ticket/change_form.html')

    def test_messages_are_empty_on_new_ticket(self, client_r, change_view):
        response = client_r.get(change_view.url)
        assert 'ticket_messages' in response.context
        messages = response.context['ticket_messages']
        assert len(messages) == 0

    def test_messages_in_context_by_requester(self, client_r,
                                              change_view, requester):
        n = 3
        [change_view.ticket.messages.create(
            content="foo %s" % i, sender=requester) for i in range(0, n)]
        response = client_r.get(change_view.url)
        messages = response.context['ticket_messages']
        assert len(messages) == n

    def test_report_in_context_by_operator(self, client_r, change_view,
                                           operator, requester):
        n = 3
        reports = [Report.objects.create(
            recipient=requester,
            ticket=change_view.ticket,
            visible_from_requester=True,
            content="foo %s" % i,
            sender=operator) for i in range(0, n)]
        response = client_r.get(change_view.url)
        messages = response.context['ticket_messages']
        assert len(messages) == n
        assert set([r.id for r in reports]) == set([m.pk for m in messages])

    def test_messages_render_by_requester(self, client_r,
                                          change_view, requester):
        n = 3
        [change_view.ticket.messages.create(
            content="foo %s" % i, sender=requester) for i in range(0, n)]
        response = client_r.get(change_view.url)
        dom = fromstring(response.content)
        for html_id in ['ticket_infos', 'tab_messages']:
            ticket_infos = dom.cssselect('#{}'.format(html_id))
            assert len(ticket_infos) == 1, "no #{} in content".format(html_id)
        assert len(dom.cssselect('#tab_messages fieldset div')) == n

    def test_reports_render_by_requester(self, client_r, change_view, operator,
                                         requester):
        n = 3
        [Report.objects.create(
            recipient=requester, ticket=change_view.ticket,
            visible_from_requester=True, content="foo %s" % i,
            sender=operator) for i in range(0, n)]
        response = client_r.get(change_view.url)
        dom = fromstring(response.content)
        for html_id in ['ticket_infos', 'tab_messages']:
            ticket_infos = dom.cssselect('#{}'.format(html_id))
            assert len(ticket_infos) == 1, "no #{} in content".format(html_id)
        assert len(dom.cssselect('#tab_messages fieldset div')) == n
