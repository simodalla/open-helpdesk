# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django.core.urlresolvers import reverse
from django.test import TestCase

from helpdesk.defaults import (HELPDESK_REQUESTERS, HELPDESK_OPERATORS,
                               HELPDESK_ADMINS)
from helpdesk.models import (Category, Tipology, Ticket, StatusChangesLog,
                             TICKET_STATUS_NEW, TICKET_STATUS_OPEN)
from .factories import (CategoryFactory, UserFactory, GroupFactory,
                        SiteFactory, TipologyFactory, TicketFactory)


class CategoryTest(TestCase):

    def test_str_method(self):
        category = Category(title="foo")
        self.assertEqual("{}".format(category), "foo")

    def test_admin_tipologies(self):
        category = CategoryFactory()
        admin_tipologies_result = '<br>'.join(
            ['<a href="{}?id={}" class="view_tipology">{}</a>'.format(
                reverse('admin:helpdesk_tipology_changelist'), t.pk, t.title)
             for t in category.tipologies.all()])
        self.assertEqual(category.admin_tipologies(), admin_tipologies_result)


class TipologyTest(TestCase):

    def test_str_method(self):
        tipology = Tipology(title="foo", category=Category(title="bar"))
        self.assertEqual("{}".format(tipology), "[bar] foo")

    def test_admin_sites(self):
        tipology = TipologyFactory(category=CategoryFactory(),
                                   sites=[SiteFactory() for i in range(0, 2)])
        admin_sites_result = '<br>'.join(
            ['<a href="{url}?id={site.id}" class="view_site">{site.domain}'
             '</a>'.format(url=reverse('admin:sites_site_changelist'), site=s)
             for s in tipology.sites.all()])
        self.assertEqual(tipology.admin_sites(), admin_sites_result)

    def test_admin_category(self):
        tipology = TipologyFactory(category=CategoryFactory(),
                                   sites=[SiteFactory() for i in range(0, 2)])
        admin_category_result = (
            '<a href="{url}?id={category.pk}" class="view_category">'
            '{category.title}</a>'.format(
                url=reverse('admin:helpdesk_category_changelist'),
                category=tipology.category))
        self.assertEqual(tipology.admin_category(), admin_category_result)


class HelpdeskUserTest(TestCase):

    @patch('helpdesk.models.HelpdeskUser.groups')
    def test_group_names_property(self, mock_groups):
        user = UserFactory()
        mock_groups.values_list.return_value = ['g1', 'g2']
        group_names = user.group_names
        self.assertEqual(group_names, ['g1', 'g2'])
        mock_groups.values_list.assert_is_called_once_with('name', flat=True)

    def test_is_requester_return_false(self):
        user = UserFactory()
        self.assertFalse(user.is_requester())

    def test_is_operator_return_false(self):
        user = UserFactory()
        self.assertFalse(user.is_operator())

    def test_is_admin_return_false(self):
        user = UserFactory()
        self.assertFalse(user.is_admin())

    @patch('helpdesk.models.settings')
    def test_is_requester_return_true(self, mock_settings):
        mock_settings.HELPDESK_REQUESTERS = HELPDESK_REQUESTERS[0]
        user = UserFactory(groups=[GroupFactory(name=HELPDESK_REQUESTERS[0])])
        self.assertTrue(user.is_requester())

    @patch('helpdesk.models.settings')
    def test_is_operator_return_true(self, mock_settings):
        mock_settings.HELPDESK_OPERATORS = HELPDESK_OPERATORS[0]
        user = UserFactory(groups=[GroupFactory(name=HELPDESK_OPERATORS[0])])
        self.assertTrue(user.is_operator())

    @patch('helpdesk.models.settings')
    def test_is_admins_return_true(self, mock_settings):
        mock_settings.HELPDESK_ADMINS = HELPDESK_ADMINS[0]
        user = UserFactory(
            groups=[GroupFactory(name=HELPDESK_ADMINS[0])])
        self.assertTrue(user.is_admin())


class OpenTicketTest(TestCase):

    def setUp(self):
        self.category = CategoryFactory(tipologies=['tip1', 'tip2'])
        self.operator = UserFactory(
            groups=[GroupFactory(name=HELPDESK_OPERATORS[0],
                                 permissions=list(HELPDESK_OPERATORS[1]))])

    def test_open_method_raise_exception_if_not_new(self):
        """
        Test that calling of open method on ticket with not "new" status raise
        an ValueError exception.
        """
        ticket = Ticket()
        ticket.status = TICKET_STATUS_NEW + 1
        self.assertRaises(ValueError, ticket.open, Mock())

    def test_open_method_set_assignee_and_open_status(self):
        """
        Test that calling of open method on ticket with new status set
        the field status to TICKET_STATUS_OPEN and set 'assignee' field
        with parameter assignee
        """
        ticket = TicketFactory(requester=self.operator,
                               tipologies=self.category.tipologies.all())
        ticket.open(self.operator)
        self.assertEqual(ticket.status, TICKET_STATUS_OPEN)
        self.assertEqual(ticket.assignee, self.operator)

    def test_open_method_create_status_changelog_related_object(self):
        ticket = TicketFactory(requester=self.operator,
                               tipologies=self.category.tipologies.all())
        ticket.open(self.operator)
        changelog = ticket.status_changelogs.latest()
        self.assertEqual(changelog.changer.pk, self.operator.pk)
        self.assertEqual(changelog.status_from, TICKET_STATUS_NEW)
        self.assertEqual(changelog.status_to, TICKET_STATUS_OPEN)


class PendingTicketTest(TestCase):

    def setUp(self):
        self.category = CategoryFactory(tipologies=['tip1', 'tip2'])
        self.operator = UserFactory(
            groups=[GroupFactory(name=HELPDESK_OPERATORS[0],
                                 permissions=list(HELPDESK_OPERATORS[1]))])
        self.ticket = TicketFactory(requester=self.operator,
                                    tipologies=self.category.tipologies.all(),
                                    status=TICKET_STATUS_OPEN)

    def test_put_on_pending_method_raise_exception_if_not_open(self):
        """
        Test that calling of "put_on_pending" method on ticket with not "open"
        status raise an ValueError exception.
        """
        self.ticket.status = TICKET_STATUS_OPEN + 1
        self.assertRaises(ValueError, self.ticket.put_on_pending, Mock())


class StatusChagesLogTest(TestCase):

    def setUp(self):
        category = CategoryFactory(tipologies=['tip1'])
        self.ticket = TicketFactory(requester=UserFactory(),
                                    tipologies=category.tipologies.all())

    def test_str_method(self):
        created = Mock()
        fake_date = '10/09/1980'
        created.strftime.return_value = fake_date
        changelog = StatusChangesLog()
        changelog.ticket = self.ticket
        changelog.created = created
        changelog.status_from = TICKET_STATUS_NEW
        changelog.status_to = TICKET_STATUS_OPEN
        self.assertEqual(str(changelog), '{} {}: New ==> Open'.format(
            self.ticket.pk, fake_date, TICKET_STATUS_NEW, TICKET_STATUS_OPEN))
