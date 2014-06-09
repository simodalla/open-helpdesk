# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.sites.models import Site

from helpdesk.defaults import HELPDESK_REQUESTERS
from helpdesk.models import Ticket, PRIORITY_NORMAL, Message
from tests.factories import (UserFactory, GroupFactory, CategoryFactory,
                             TipologyFactory, TicketFactory)
from .base import FunctionalTest


class RequesterTicketsTest(FunctionalTest):

    def setUp(self):
        super(RequesterTicketsTest, self).setUp()
        self.requester = UserFactory(
            groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
                                 permissions=list(HELPDESK_REQUESTERS[1]))])
        self.client.login(username=self.requester.username,
                          password='default')
        self.category = CategoryFactory()
        site = Site.objects.get(pk=1)
        self.tipologies = [
            TipologyFactory(sites=(site,), category=self.category)
            for i in range(0, 2)]
        self.create_pre_authenticated_session(self.requester)
        self.ticket_content = ("foo " * 20).rstrip()

    def test_add_booking_type(self):

        self.browser.get(
            self.get_url(admin_urlname(Ticket._meta, 'add')))
        for t in self.tipologies:
            self.browser.find_element_by_css_selector(
                "#id_tipologies_from option[value='{}']".format(t.pk)).click()
        self.browser.find_element_by_css_selector(
            '#id_tipologies_add_link').click()
        # set content of tipology
        self.set_content_to_tinymce(self.ticket_content)
        # select priority to PRIORITY_NORMAL
        self.browser.find_element_by_css_selector(
            "#id_priority input[value='{}']".format(PRIORITY_NORMAL)).click()
        self.browser.find_element_by_name('_save').click()
        ticket = Ticket.objects.latest()
        self.assertEqual(ticket.requester.pk, self.requester.pk)
        self.assertEqual(ticket.priority, PRIORITY_NORMAL)
        self.assertIn(self.ticket_content, ticket.content)
        self.assertEqual(set(ticket.tipologies.all()),
                         set(self.tipologies))
        self.browser.get(
            self.get_url(admin_urlname(Ticket._meta, 'change'),
                         args=(ticket.pk,)))

    # def test_change_booking_type(self):
    #     from django.conf import settings
    #     settings.DEBUG = True
    #     ticket = TicketFactory(content=self.ticket_content,
    #                            requester=self.requester,
    #                            tipologies=self.tipologies)
    #     [Message.objects.create(ticket=ticket, sender=self.requester,
    #                             content="bla bla bla") for i in range(0, 2)]
    #     self.browser.get(
    #         self.get_url(admin_urlname(Ticket._meta, 'change'),
    #                      args=(ticket.pk,)))
    #     import ipdb
    #     ipdb.set_trace()
