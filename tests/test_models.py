# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from future.builtins import str

import datetime
import os.path
import six

import pytest

try:
    from unittest.mock import patch, Mock, ANY, PropertyMock
except ImportError:
    from mock import patch, Mock, ANY, PropertyMock

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.test import TestCase

from mezzanine.utils.sites import current_site_id

from openhelpdesk.defaults import (HELPDESK_REQUESTERS, HELPDESK_OPERATORS,
                                   HELPDESK_ADMINS)
from openhelpdesk.models import (Category, Tipology, Ticket, StatusChangesLog,
                                 PRIORITY_LOW, PendingRange, SiteConfiguration)
from openhelpdesk.core import (TicketIsNotNewError, TicketIsNotOpenError,
                               TicketIsClosedError, TicketIsNotPendingError,
                               TicketIsNewError)
from .factories import (CategoryFactory, UserFactory, GroupFactory,
                        SiteFactory, TipologyFactory, TicketFactory,
                        OrganizationSettingF, SubteamF)

from openhelpdesk.core import HelpdeskUser

from . import factories


TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '../openhelpdesk/templates/')


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
        tipology = TipologyFactory(title="foo",
                                   category=CategoryFactory(title="bar"))
        self.assertEqual("{}".format(tipology), "[bar] foo")

    # TODO: move this test to test_admins
    @pytest.mark.xfail(reason="method admin_sites is moved to TipologyAdmin"
                              " method ld_sites")
    def test_admin_sites(self):
        tipology = TipologyFactory(category=CategoryFactory(),
                                   sites=[SiteFactory() for i in range(0, 2)])
        admin_sites_result = '<br>'.join(
            ['<a href="{url}?id={site.id}" class="view_site">{site.domain}'
             '</a>'.format(url=reverse('admin:sites_site_changelist'), site=s)
             for s in tipology.sites.all()])
        self.assertEqual(tipology.admin_sites(), admin_sites_result)

    # TODO: move this test to test_admins
    @pytest.mark.xfail(reason="method admin_category is moved to TipologyAdmin"
                              " method ld_category")
    def test_admin_category(self):
        tipology = TipologyFactory(category=CategoryFactory(),
                                   sites=[SiteFactory() for i in range(0, 2)])
        admin_category_result = (
            '<a href="{url}?id={category.pk}" class="view_category">'
            '{category.title}</a>'.format(
                url=reverse('admin:openhelpdesk_category_changelist'),
                category=tipology.category))
        self.assertEqual(tipology.admin_category(), admin_category_result)


class HelpdeskUserTest(TestCase):

    @patch('django.contrib.auth.models.User.groups')
    def test_group_names_property(self, mock_groups):
        user = UserFactory()
        mock_groups.values_list.return_value = ['g1', 'g2']
        hu = HelpdeskUser(user)
        group_names = hu.group_names
        self.assertEqual(group_names, ['g1', 'g2'])
        mock_groups.values_list.assert_called_once_with('name', flat=True)

    def test_is_requester_return_false(self):
        hu = HelpdeskUser(UserFactory())
        self.assertFalse(hu.is_requester())

    def test_is_operator_return_false(self):
        hu = HelpdeskUser(UserFactory())
        self.assertFalse(hu.is_operator())

    def test_is_admin_return_false(self):
        hu = HelpdeskUser(UserFactory())
        self.assertFalse(hu.is_admin())

    @patch('openhelpdesk.models.settings')
    def test_is_requester_return_true(self, mock_settings):
        mock_settings.HELPDESK_REQUESTERS = HELPDESK_REQUESTERS[0]
        hu = HelpdeskUser(
            UserFactory(groups=[GroupFactory(name=HELPDESK_REQUESTERS[0])]))
        self.assertTrue(hu.is_requester())

    @patch('openhelpdesk.models.settings')
    def test_is_operator_return_true(self, mock_settings):
        mock_settings.HELPDESK_OPERATORS = HELPDESK_OPERATORS[0]
        hu = HelpdeskUser(
            UserFactory(groups=[GroupFactory(name=HELPDESK_OPERATORS[0])]))
        self.assertTrue(hu.is_operator())

    @patch('openhelpdesk.models.settings')
    def test_is_admins_return_true(self, mock_settings):
        mock_settings.HELPDESK_ADMINS = HELPDESK_ADMINS[0]
        hu = HelpdeskUser(UserFactory(
            groups=[GroupFactory(name=HELPDESK_ADMINS[0])]))
        self.assertTrue(hu.is_admin())


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


@pytest.fixture
def unsaved_ticket(requester):
    ticket = Ticket()
    ticket.priority = PRIORITY_LOW
    ticket.content = 'foo ' * 10
    ticket.requester = requester
    return ticket


@pytest.fixture
def request_for_email(rf):
    request_obj = rf.get('/fake_ticket_created/')
    return request_obj


# noinspection PyUnresolvedReferences
@pytest.mark.django_db
class TestTicketModel(object):

    def test_organization_property_return_none_with_differente_email_domain(
            self, requester, new_ticket):
        org = OrganizationSettingF()
        different_domain = 'fake-domain.com'
        assert org.email_domain != different_domain
        new_ticket.requester.email = 'user@' + different_domain
        assert new_ticket.organization is None

    def test_organization_property_return_organization_obj_with_same_email_domain(
            self, requester, new_ticket):
        org = OrganizationSettingF()
        assert (
            org.email_domain ==
            new_ticket.requester.email[new_ticket.requester.email.find('@')+1:])
        assert new_ticket.organization == org


    def test_custom_save_set_insert_by_to_requester_by_default(
            self, requester, unsaved_ticket):
        unsaved_ticket.save()
        assert unsaved_ticket.requester_id == requester.id
        assert unsaved_ticket.insert_by_id == requester.id

    def test_custom_save_set_insert_by_field(self, unsaved_ticket, operator):
        unsaved_ticket.insert_by = operator
        unsaved_ticket.save()
        assert unsaved_ticket.insert_by_id == operator.pk

    def test_save_set_site_to_current_site(self, unsaved_ticket):
        unsaved_ticket.save()
        assert unsaved_ticket.site_id == current_site_id()

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

    def test_remove_from_pending_raise_exception_if_ticket_is_not_pending(
            self, opened_ticket, operator):
        """
        Test that calling "remove_from_pending" on a ticket that not in
        'pending' status raise an TicketIsNotPendingError exception

        :type opened_ticket: Ticket
        :type operator: UserFactory
        """
        assert opened_ticket != Ticket.STATUS.pending
        with pytest.raises(TicketIsNotPendingError):
            opened_ticket.remove_from_pending(operator)

    def test_remove_from_pending_set_status_to_open(
            self, pending_ticket, operator):
        """
        Test that calling "remove_from_pending" on a pending ticket set the
        status to open

        :type pending_ticket: Ticket
        :type operator: UserFactory
        """
        assert pending_ticket.status == Ticket.STATUS.pending
        pending_ticket.remove_from_pending(operator)
        assert pending_ticket.status == Ticket.STATUS.open

    def test_remove_from_pending_create_statuschangelog_object(
            self, pending_ticket, operator):
        """
        Test that calling "remove_from_pending" on a pending ticket create
        the relative StatusChangelog object

        :type pending_ticket: Ticket
        :type operator: UserFactory
        """
        assert pending_ticket.status == Ticket.STATUS.pending
        statuschangelog = pending_ticket.remove_from_pending(operator)
        assert statuschangelog.ticket == pending_ticket
        assert statuschangelog.before == Ticket.STATUS.pending
        assert statuschangelog.after == Ticket.STATUS.open

    def test_remove_from_pending_update_pending_range_object(
            self, pending_ticket, operator):
        """
        Test that calling "remove_from_pending" on a pending ticket, related
        PendingRange object is updated.

        :type pending_ticket: Ticket
        :type operator: UserFactory
        """
        assert pending_ticket.status == Ticket.STATUS.pending
        pending_range = pending_ticket.pending_ranges.get(end__isnull=True)
        statuschangelog = pending_ticket.remove_from_pending(operator)
        assert (PendingRange.objects.get(pk=pending_range.pk).end ==
                statuschangelog.updated)

    @pytest.mark.parametrize("status,exception", [
        (Ticket.STATUS.closed, TicketIsClosedError),
        (Ticket.STATUS.new, TicketIsNewError)])
    def test_closing_with_status_that_raises_exceptions(
            self, status, exception, new_ticket, operator):
        """
        Test the exceptions raised by "closing" method under wrong status

        :type new_ticket: Ticket
        :type operator: UserFactory
        """
        new_ticket.status = status
        new_ticket.save()
        with pytest.raises(exception):
            new_ticket.closing(operator)

    @pytest.mark.parametrize("status", [
        Ticket.STATUS.open, Ticket.STATUS.pending])
    def test_closing_set_status_to_close(
            self, status, pending_ticket, operator):
        """
        Test that calling "closing" on a open or pending ticket set the
        status to open

        :type pending_ticket: Ticket
        :type operator: UserFactory
        """
        pending_ticket.status = status
        pending_ticket.save()
        pending_ticket.closing(operator)
        assert pending_ticket.status == Ticket.STATUS.closed

    @pytest.mark.parametrize("status", [
        Ticket.STATUS.open, Ticket.STATUS.pending])
    def test_closing_create_statuschangelog_object(
            self, status, pending_ticket, operator):
        """
        Test that calling "closing" on a open or pending ticket create
        the relative StatusChangelog object

        :type pending_ticket: Ticket
        :type operator: UserFactory
        """
        pending_ticket.status = status
        pending_ticket.save()
        statuschangelog = pending_ticket.closing(operator)
        assert statuschangelog.ticket == pending_ticket
        assert statuschangelog.before == status
        assert statuschangelog.after == Ticket.STATUS.closed

    def test_closing_update_relative_pendingrange_object(
            self, pending_ticket, operator):
        """
        Test that calling "closing" on a pending ticket update the relative
        PendingRange object

        :type pending_ticket: Ticket
        :type operator: UserFactory
        """
        pending_range = pending_ticket.pending_ranges.get(end__isnull=True)
        statuschangelog = pending_ticket.closing(operator)
        assert (PendingRange.objects.get(pk=pending_range.pk).end ==
                statuschangelog.updated)

    def get_site_config_for_ticket(
            self, ticket, email_addr_from=''):
        defaults = {'_email_addr_from': email_addr_from}
        site_conf, created = SiteConfiguration.objects.get_or_create(
            site=ticket.site, defaults=defaults)
        return site_conf

    @patch('openhelpdesk.models.send_mail_template')
    def test_send_email_to_operators_addr_from_without_matchin_configsite(
            self, mock_send_email, initialized_ticket, request_for_email):
        """
        :param initialized_ticket: Ticket already intialized
        :type initialized_ticket: openhelpdesk.models.Ticket
        """
        server_email = 'server@example.com'
        with patch('openhelpdesk.models.SiteConfiguration'
                   '.get_no_site_email_addr_from', return_value=server_email):
            initialized_ticket.send_email_to_operators_on_adding(
                request_for_email)

        mock_send_email.assert_called_once_with(ANY, ANY, server_email, ANY,
                                                context=ANY, attachments=ANY)

    @patch('openhelpdesk.models.send_mail_template')
    def test_send_email_to_operators_add_from_set_by_site_configuration(
            self, mock_send_email, initialized_ticket, request_for_email):
        """
        :param initialized_ticket: Ticket already intialized
        :type initialized_ticket: openhelpdesk.models.Ticket
        """
        site_email = 'helpdesk@example.com'
        self.get_site_config_for_ticket(
            initialized_ticket, email_addr_from=site_email)

        initialized_ticket.send_email_to_operators_on_adding(request_for_email)

        mock_send_email.assert_called_once_with(ANY, ANY, site_email, ANY,
                                                context=ANY, attachments=ANY)

    @patch('openhelpdesk.models.send_mail_template')
    def test_send_email_to_operators_addrs_to_without_matchin_configsite(
            self, mock_send_email, initialized_ticket, request_for_email):
        """
        :param initialized_ticket: Ticket already intialized
        :type initialized_ticket: openhelpdesk.models.Ticket
        """
        site_ops_email = ['operator1@example.com', 'operator2@example.com']
        with patch('openhelpdesk.models.SiteConfiguration'
                   '.get_no_site_email_addrs_to', return_value=site_ops_email):
            initialized_ticket.send_email_to_operators_on_adding(
                request_for_email)

        mock_send_email.assert_called_once_with(ANY, ANY, ANY, site_ops_email,
                                                context=ANY, attachments=ANY)

    @patch('openhelpdesk.models.send_mail_template')
    def test_send_email_to_operators_add_to_set_by_site_configuration(
            self, mock_send_email, initialized_ticket, request_for_email):
        """
        :param initialized_ticket: Ticket already intialized
        :type initialized_ticket: openhelpdesk.models.Ticket
        """
        site_ops_email = ['ced@example.com', 'support@example.com']
        self.get_site_config_for_ticket(initialized_ticket)
        with patch(
                'openhelpdesk.models.SiteConfiguration.email_addrs_to',
                new_callable=PropertyMock(return_value=site_ops_email)):
            initialized_ticket.send_email_to_operators_on_adding(
                request_for_email)

        mock_send_email.assert_called_once_with(ANY, ANY, ANY, site_ops_email,
                                                context=ANY, attachments=ANY)

    @patch('openhelpdesk.models.send_mail_template')
    def test_send_email_to_operators_context_set(
            self, mock_send_email, initialized_ticket, request_for_email):
        """
        :param initialized_ticket: Ticket already intialized
        :type initialized_ticket: openhelpdesk.models.Ticket
        """
        site_ops_email = ['ced@example.com', 'support@example.com']
        self.get_site_config_for_ticket(initialized_ticket)
        change_url = reverse(admin_urlname(initialized_ticket._meta, 'change'),
                             args=(initialized_ticket.pk,))
        context = {'ticket_name': initialized_ticket._meta.verbose_name,
                   'ticket': initialized_ticket,
                   'request': request_for_email,
                   'change_url': change_url}

        with patch('openhelpdesk.models.SiteConfiguration'
                   '.email_addrs_to', return_value=site_ops_email):
            initialized_ticket.send_email_to_operators_on_adding(
                request_for_email)

        mock_send_email.assert_called_once_with(
            ANY, ANY, ANY, ANY, context=context, attachments=ANY)

    @patch('openhelpdesk.models.send_mail_template')
    def test_send_email_to_operators_call_with_right_template(
            self, mock_send_email, initialized_ticket):
        """
        :param initialized_ticket: Ticket already intialized
        :type initialized_ticket: openhelpdesk.models.Ticket
        """
        template = ("openhelpdesk/email/ticket/"
                    "ticket_operators_creation")
        template_paths = [
            os.path.join(TEMPLATES_DIR, template + '.%s' % tpl_type)
            for tpl_type in ('html', 'txt')]
        ticket = initialized_ticket

        for path in template_paths:
            assert os.path.exists(path), ("File {} doesn't"
                                          " exists.".format(path))

        ticket.send_email_to_operators_on_adding(request_for_email)

        mock_send_email.assert_called_once_with(ANY, template, ANY, ANY,
                                                context=ANY, attachments=ANY)

    @patch('openhelpdesk.models.send_mail_template')
    def test_send_email_to_operators_call_subject_template(
            self, mock_send_email, initialized_ticket):
        """
        :param initialized_ticket: Ticket already intialized
        :type initialized_ticket: openhelpdesk.models.Ticket
        """
        template = ("openhelpdesk/email/ticket/"
                    "ticket_operators_creation_subject.html")
        template_path = os.path.join(TEMPLATES_DIR, template)
        ticket = initialized_ticket
        subject = 'foo subject'

        assert os.path.exists(template_path), ("File {} doesn't exists"
                                               ".".format(template_path))
        with patch('openhelpdesk.models.subject_template',
                   return_value=subject) as mock_subj:
            ticket.send_email_to_operators_on_adding(request_for_email)

        mock_subj.assert_called_once_with(
            template, {'ticket_name': ticket._meta.verbose_name.lower(),
                       'username': ticket.requester.username})

        mock_send_email.assert_called_once_with(subject, ANY, ANY, ANY,
                                                context=ANY, attachments=ANY)


class TestSiteConfigurationModel(object):
    @pytest.mark.skipif(six.PY2, reason="requires python3")
    def test_str_method(self):
        with patch.object(SiteConfiguration, 'site',
                          __str__=lambda x: 'site foo'):
            site_conf = SiteConfiguration()
            assert site_conf.__str__() == 'site foo'

    @pytest.mark.skipif(six.PY3, reason="requires python2")
    def test_unicode_method(self):
        with patch.object(SiteConfiguration, 'site',
                          __unicode__=lambda x: 'site foo'):
            site_conf = SiteConfiguration()
            assert str(site_conf) == 'site foo'

    def test_email_addrs_to_return_list_of_not_null_email_addresses(
            self):
        site_conf = SiteConfiguration()
        site_conf._email_addr_to_1 = 'foo1@example.com'
        site_conf._email_addr_to_2 = 'foo2@example.com'
        site_conf._email_addr_to_3 = 'foo3@example.com'
        assert set(site_conf.email_addrs_to) == {'foo1@example.com',
                                                 'foo2@example.com',
                                                 'foo3@example.com'}

    def test_mail_addrs_to_return_list_of_not_duplicate_email_addresses(self):
        site_conf = SiteConfiguration()
        site_conf._email_addr_to_1 = 'foo1@example.com'
        site_conf._email_addr_to_2 = 'foo1@example.com'
        site_conf._email_addr_to_3 = 'foo1@example.com'
        assert set(site_conf.email_addrs_to) == {'foo1@example.com'}

    def test_mail_addrs_to_return_empty_list_if_all_null_email_addresses(self):
        site_conf = SiteConfiguration()
        assert site_conf.email_addrs_to == list()

    def test_email_add_from_return_field_value_isnt_none(self):
        site_conf = SiteConfiguration()
        site_conf._email_addr_from = 'helpdesk@example.com'
        assert site_conf.email_addr_from == 'helpdesk@example.com'

    def test_email_add_from_return_settings_server_email(self):
        site_conf = SiteConfiguration()
        site_conf._email_addr_from = None
        with patch('openhelpdesk.models.settings',
                   SERVER_EMAIL='bar@example.com'):
            assert site_conf.email_addr_from == 'bar@example.com'

    def test_get_no_site_email_add_from_return_settings_server_email(self):
        with patch('openhelpdesk.models.settings',
                   SERVER_EMAIL='bar@example.com'):
            assert (SiteConfiguration.get_no_site_email_addr_from()
                    == 'bar@example.com')


# noinspection PyUnresolvedReferences
@pytest.mark.django_db
class TestTeammateSettingModels:

    def test_add_to_subteam_on_default_subteam_saving(self):
        """
        Test that on saving a teammatesetting with defauaul subteam add succrent
        teaamate to teammates of subteam selected
        """
        subteam = factories.SubteamF()
        assert subteam.teammates.count() == 0
        teammate = factories.TeammateSettingF()
        teammate.default_subteam = subteam
        teammate.save()
        assert subteam.teammates.count() == 1, "Subteam don'n have teammates"
        assert teammate.user in subteam.teammates.all()
        # import ipdb
        # ipdb.set_trace()
