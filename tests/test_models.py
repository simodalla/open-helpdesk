# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime

import pytest

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from django.core.urlresolvers import reverse
from django.test import TestCase

from helpdesk.defaults import (HELPDESK_REQUESTERS, HELPDESK_OPERATORS,
                               HELPDESK_ADMINS)
from helpdesk.models import Category, Tipology, Ticket, StatusChangesLog
from helpdesk.core import (TicketIsNotNewError, TicketIsNotOpenError,
                           TicketIsClosedError, TicketStatusError)
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
        ticket.status = Ticket.STATUS.closed
        self.assertRaisesMessage(
            TicketIsNotNewError, 'Ticket not in status "New"',
            ticket.opening, Mock())

    def test_open_method_set_assignee_and_open_status(self):
        """
        Test that calling of open method on ticket with new status set
        the field status to TICKET_STATUS_OPEN and set 'assignee' field
        with parameter assignee
        """
        ticket = TicketFactory(requester=self.operator,
                               tipologies=self.category.tipologies.all())
        ticket.opening(self.operator)
        self.assertEqual(ticket.status, Ticket.STATUS.open)
        self.assertEqual(ticket.assignee, self.operator)

    def test_open_method_create_status_changelog_related_object(self):
        ticket = TicketFactory(requester=self.operator,
                               tipologies=self.category.tipologies.all())
        ticket.opening(self.operator)
        changelog = ticket.status_changelogs.latest()
        self.assertEqual(changelog.changer.pk, self.operator.pk)
        self.assertEqual(changelog.before, Ticket.STATUS.new)
        self.assertEqual(changelog.after, Ticket.STATUS.open)


class ClosedTicketTest(TestCase):

    def setUp(self):
        self.category = CategoryFactory(tipologies=['tip1', 'tip2'])
        self.operator = UserFactory(
            groups=[GroupFactory(name=HELPDESK_OPERATORS[0],
                                 permissions=list(HELPDESK_OPERATORS[1]))])
        self.ticket = TicketFactory(requester=self.operator,
                                    tipologies=self.category.tipologies.all(),
                                    status=Ticket.STATUS.open)

    def test_closing_method_raise_exception_if_ticket_is_already_closed(self):
        self.ticket.status = Ticket.STATUS.closed
        self.assertRaisesMessage(
            TicketIsClosedError, 'Ticket is already in "Closed" status',
            self.ticket.closing, Mock())

    def test_closing_method_raise_exception_if_ticket_is_new(self):
        self.ticket.status = Ticket.STATUS.new
        self.assertRaisesMessage(
            TicketStatusError, 'The ticket is still open',
            self.ticket.closing, Mock())

    def test_closing_method_set_closed_status(self):
        """
        Test that calling of "closing" method on ticket with open status
        set the field status to Ticket.STATUS.closed
        """
        self.ticket.closing(self.operator)
        self.assertEqual(self.ticket.status, Ticket.STATUS.closed)

    def test_closing_method_create_status_changelog_related_object(self):
        """
        Test that calling of "closing" method on ticket with open status
        create an related StatusChangesLog object with right data on fields
        """
        status_before = self.ticket.status
        self.ticket.closing(self.operator)
        changelog = self.ticket.status_changelogs.latest()
        self.assertEqual(changelog.changer.pk, self.operator.pk)
        self.assertEqual(changelog.before, status_before)
        self.assertEqual(changelog.after, Ticket.STATUS.closed)


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
        changelog.before = Ticket.STATUS.new
        changelog.after = Ticket.STATUS.open
        self.assertEqual(str(changelog), '{} {}: new ==> open'.format(
            self.ticket.pk, fake_date))


@pytest.mark.django_db
class TestTicketStutusManagements(object):
    def test_put_on_pending_method_raise_exception_if_ticket_not_open(
            self, new_ticket, operator):
        """
        Test that calling of "put_on_pending" method on ticket with not "open"
        status raise an TicketIsNotOpenError exception.
        """
        assert new_ticket.status != Ticket.STATUS.open
        with pytest.raises(TicketIsNotOpenError):
            new_ticket.put_on_pending(operator)

    def test_put_on_pending_method_set_pending_status_to_ticket(
            self, opened_ticket, operator):
        """
        Test that calling of "put_on_pending" method on ticket with open status
        set the field status to Ticket.STATUS.pending
        """
        assert opened_ticket.status == Ticket.STATUS.open
        opened_ticket.put_on_pending(operator)
        # ticket = Ticket.objects.get()
        assert opened_ticket.status == Ticket.STATUS.pending

    def test_put_on_pending_method_create_statuschangelog_obj(
            self, opened_ticket, operator):
        """
        Test that calling of "put_on_pending" method on ticket with open status
        create an StatusChangelog object.
        """
        assert opened_ticket.status == Ticket.STATUS.open
        pre_statuschangelogs = opened_ticket.status_changelogs.count()
        opened_ticket.put_on_pending(operator)
        qs_statuschangelogs = opened_ticket.status_changelogs.all()
        assert qs_statuschangelogs.count() == pre_statuschangelogs + 1
        statuschangelog = qs_statuschangelogs.latest()
        assert statuschangelog.before == Ticket.STATUS.open
        assert statuschangelog.after == Ticket.STATUS.pending
        assert statuschangelog.changer.pk == operator.pk

    def test_put_on_pending_method_create_pendingrange_obj(
            self, opened_ticket, operator):
        """
        Test that calling of "put_on_pending" method on ticket with open status
        create an PendingRange object.
        """
        assert opened_ticket.status == Ticket.STATUS.open
        pre_pendingrange = opened_ticket.pending_ranges.count()
        opened_ticket.put_on_pending(operator)
        qs_pendingrange = opened_ticket.pending_ranges.all()
        assert qs_pendingrange.count() == pre_pendingrange + 1
        statuschangelog = opened_ticket.status_changelogs.latest()
        pendingrange = qs_pendingrange.latest()
        assert pendingrange.start == statuschangelog.created
        assert pendingrange.end is None
        assert pendingrange.estimated_end is None
        assert pendingrange.object_id == opened_ticket.id

    def test_put_on_pending_method_create_pendingrange_obj_with_estimated_date(
            self, opened_ticket, operator):
        """
        Test that calling of "put_on_pending" method on ticket with open status
        create an PendingRange object.
        """
        assert opened_ticket.status == Ticket.STATUS.open
        pre_pendingrange = opened_ticket.pending_ranges.count()
        estimated_date = (datetime.date.today()
                          + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
        opened_ticket.put_on_pending(operator,
                                     estimated_end_date=estimated_date)
        qs_pendingrange = opened_ticket.pending_ranges.all()
        assert qs_pendingrange.count() == pre_pendingrange + 1
        statuschangelog = opened_ticket.status_changelogs.latest()
        pendingrange = qs_pendingrange.latest()
        assert pendingrange.start == statuschangelog.created
        assert pendingrange.end is None
        assert (pendingrange.estimated_end.strftime('%Y-%m-%d') ==
                estimated_date)
        assert pendingrange.object_id == opened_ticket.id




