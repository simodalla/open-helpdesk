# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import VERSION as DJANGO_VERSION
from django.test import TestCase
from lxml.html import fromstring

from helpdesk.defaults import (HELPDESK_REQUESTERS,
                               HELPDESK_OPERATORS,
                               HELPDESK_TICKET_MAX_TIPOLOGIES)
from helpdesk.models import Ticket, Tipology, Category

from .helpers import AdminTestMixin
from .factories import (
    UserFactory, CategoryFactory, GroupFactory, SiteFactory, TicketFactory,
    TipologyFactory)


class FunctionalTicketByRequesterTest(AdminTestMixin, TestCase):
    def setUp(self):
        self.requester = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        self.client.login(username=self.requester.username, password='default')
        tipology_names = ['tip{}'.format(i) for i
                          in range(0, HELPDESK_TICKET_MAX_TIPOLOGIES-1)]
        self.category = CategoryFactory(tipologies=tipology_names)
        self.post_data = {'content': 'helpdesk_content',
                          'tipologies': self.category.tipology_pks,
                          'priority': 1}

    def test_adding_ticket_set_requester_field(self):
        """
        Test that adding new ticket, the field requester is setted with
        logged user.
        """
        self.client.post(self.get_url(Ticket, 'add'), data=self.post_data)
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.requester.pk, self.requester.pk)

    def test_changelist_view_is_filtered(self):
        """
        Test that the changelist is filtered by tickets with requester's field
        matching to logged user.
        """
        n = 3
        for user in [self.requester, UserFactory(
                groups=self.requester.groups.all())]:
            [TicketFactory(requester=user,
                           tipologies=self.category.tipologies.all())
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
        assert (len(self.post_data['tipologies'])
                < HELPDESK_TICKET_MAX_TIPOLOGIES)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertRedirects(response, self.get_url(Ticket, 'changelist'))

    def test_form_with_equals_tipologies_fields_is_validate(self):
        tipology_names = ['tip{}'.format(i) for i
                          in range(0, HELPDESK_TICKET_MAX_TIPOLOGIES)]
        category = CategoryFactory(tipologies=tipology_names)
        self.post_data['tipologies'] = category.tipology_pks
        assert (len(self.post_data['tipologies'])
                == HELPDESK_TICKET_MAX_TIPOLOGIES)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertRedirects(response, self.get_url(Ticket, 'changelist'))

    def test_form_with_more_tipologies_fields_is_not_validate(self):
        tipology_names = ['tip{}'.format(i) for i
                          in range(0, HELPDESK_TICKET_MAX_TIPOLOGIES + 1)]
        category = CategoryFactory(tipologies=tipology_names)
        self.post_data['tipologies'] = category.tipology_pks
        assert (len(self.post_data['tipologies'])
                > HELPDESK_TICKET_MAX_TIPOLOGIES)
        response = self.client.post(self.get_url(Ticket, 'add'),
                                    data=self.post_data)
        self.assertEqual(response.status_code, 200)
        self.assertAdminFormError(response, 'tipologies',
                                  'Too many tipologies selected. You can'
                                  ' select a maximum of {}.'.format(
                                      HELPDESK_TICKET_MAX_TIPOLOGIES))

    # def test_for_fieldset_object(self):
    #     self.client.get(self.get_url(Ticket, 'add'))
    #     t = TicketFactory(requester=self.requester,
    #                       tipologies=self.category.tipologies.all())
    #     self.client.get(self.get_url(Ticket, 'change', args=(t.pk,)))


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


class OpenTicketViewTest(AdminTestMixin, TestCase):

    def setUp(self):
        self.operator = UserFactory(
            groups=[GroupFactory(name=HELPDESK_OPERATORS[0],
                                 permissions=list(HELPDESK_OPERATORS[1]))])
        self.client.login(username=self.operator.username,
                          password='default')
        self.category = CategoryFactory(tipologies=['tip1'])
        self.ticket = TicketFactory(
            requester=self.operator, tipologies=self.category.tipologies.all())

    def test_for_call_view(self):
        response = self.client.get(
            self.get_url(Ticket, 'open', kwargs={'pk': self.ticket.pk}))
        print(response)
