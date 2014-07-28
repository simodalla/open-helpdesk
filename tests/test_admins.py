# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest

import pytest

try:
    from unittest.mock import patch, Mock, ANY
except ImportError:
    from mock import patch, Mock, ANY

from django import VERSION as DJANGO_VERSION
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from helpdesk.admin import TicketAdmin, ReportAdmin, ReportTicketInline
from helpdesk.models import Ticket, StatusChangesLog, Report, Source

from .helpers import get_mock_request, get_mock_helpdeskuser


class TicketTest(unittest.TestCase):

    def setUp(self):
        self.ticket_admin = TicketAdmin(Ticket, AdminSite)

    @patch('helpdesk.admin.HelpdeskUser.objects.get',
           return_value=get_mock_helpdeskuser())
    def test_get_request_helpdeskuser(self, mock_get_req_hpu):
        user = self.ticket_admin.get_request_helpdeskuser(get_mock_request(1))
        mock_get_req_hpu.assert_called_once_with(pk=1)
        self.assertEqual(user, mock_get_req_hpu.return_value)


@patch('helpdesk.admin.TicketAdmin.get_request_helpdeskuser')
class TicketMethodsByRequesterTypeTest(unittest.TestCase):

    def setUp(self):
        self.ticket_admin = TicketAdmin(Ticket, AdminSite)
        self.fake_pk = 1

    def get_queryset_to_patch(self):
        return 'django.contrib.admin.ModelAdmin.{}'.format(
            'queryset' if DJANGO_VERSION < (1, 6) else 'get_queryset')

    def test_field_requester_not_in_form_if_requester_in_request(
            self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(requester=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertNotIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_operator_in_request(
            self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(
            operator=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_field_requester_not_in_form_if_admin_in_request(
            self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(admin=True)
        fieldeset = self.ticket_admin.get_fieldsets(get_mock_request())
        self.assertIn('requester', fieldeset[0][1]['fields'])

    def test_queryset_is_not_filterd_if_is_operator(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(operator=True)
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        self.assertTrue(result is qs)

    def test_queryset_is_not_filterd_if_is_admin(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(admin=True)
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        self.assertTrue(result is qs)

    def test_queryset_is_not_filterd_if_is_superuser(self, mock_get_req_hpu):
        mock_get_req_hpu.return_value = get_mock_helpdeskuser(superuser=True)
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        self.assertTrue(result is qs)

    def test_queryset_is_not_filterd_if_is_requester(self, mock_get_req_hpu):
        helpdesk_user = get_mock_helpdeskuser(requester=True)
        mock_get_req_hpu.return_value = helpdesk_user
        qs = Mock()
        with patch(self.get_queryset_to_patch(), return_value=qs):
            result = self.ticket_admin.get_queryset(
                get_mock_request(self.fake_pk))
        qs.filter.assert_called_once_with(requester=helpdesk_user)
        self.assertFalse(result is qs)


# @pytest.fixture
# def ticket_admin_change_view(rf_with_helpdeskuser, monkeypatch):
#     monkeypatch.setattr('helpdesk.admin.TicketAdmin.get_request_helpdeskuser',
#                         lambda self, request: request.user)
#     return rf_with_helpdeskuser, TicketAdmin(Ticket, AdminSite), 1


@pytest.fixture
def ticket_admin_util(model_admin_util):

    model_admin_util.model_admin = TicketAdmin(Ticket, AdminSite)
    model_admin_util.model_admin.message_user = Mock(name='message_user')
    model_admin_util.obj = Mock(spec=Ticket)

    return model_admin_util


@pytest.mark.target
class TestTicketAdmin(object):

    @patch('helpdesk.admin.StatusChangesLog', spec_set=StatusChangesLog)
    @patch('django.contrib.admin.ModelAdmin.change_view')
    def test_view_calls_has_custom_extra_content(
            self, mock_cv, mock_sclog, ticket_admin_util):
        messages = [1, 2, 3]
        statuschangelogs = [1, 2, 3]
        ticket_admin_util.user.get_messages_by_ticket.return_value = messages
        mock_sclog.objects.filter.return_value.order_by.return_value = (
            statuschangelogs)
        with patch('helpdesk.models.HelpdeskUser.get_from_request',
                   return_value=ticket_admin_util.user):
            ticket_admin_util.model_admin.change_view(
                ticket_admin_util.request, ticket_admin_util.obj.pk)
        mock_cv.assert_called_once_with(
            ticket_admin_util.request, ticket_admin_util.obj.pk, form_url='',
            extra_context={'ticket_messages': messages,
                           'ticket_changelogs': statuschangelogs,
                           'helpdesk_user': ticket_admin_util.request.user})

    @pytest.mark.parametrize(
        'helpdeskuser,expected',
        [('requester', TicketAdmin.list_display),
         ('operator', (TicketAdmin.list_display +
                       TicketAdmin.operator_list_display)),
         ('admin', (TicketAdmin.list_display +
                    TicketAdmin.operator_list_display))])
    def test_custom_list_display(
            self, helpdeskuser, expected, ticket_admin_util):
        ticket_admin_util.user = helpdeskuser
        request = ticket_admin_util.request
        with patch('helpdesk.models.HelpdeskUser.get_from_request',
                   return_value=ticket_admin_util.user):
            result = ticket_admin_util.model_admin.get_list_display(request)
        assert result == expected

    @pytest.mark.parametrize(
        'helpdeskuser,expected',
        [('requester', TicketAdmin.list_filter),
         ('operator', (TicketAdmin.list_filter +
                       TicketAdmin.operator_list_filter)),
         ('admin', (TicketAdmin.list_filter +
                    TicketAdmin.operator_list_filter))])
    def test_custom_list_filter(
            self, helpdeskuser, expected, ticket_admin_util):
        ticket_admin_util.user = helpdeskuser
        request = ticket_admin_util.request
        with patch('helpdesk.models.HelpdeskUser.get_from_request',
                   return_value=ticket_admin_util.user):
            result = ticket_admin_util.model_admin.get_list_filter(request)
        assert result == expected

    def test_ld_id_return_object_id(self, ticket_admin_util):
        ticket_admin_util.obj.pk = 1
        assert 1 == ticket_admin_util.model_admin.ld_id(ticket_admin_util.obj)

    def test_ld_status_return_get_clean_content(self, ticket_admin_util):
        mock_content = Mock(return_value='content')
        ticket_admin_util.obj.get_clean_content = mock_content
        assert 'content' == ticket_admin_util.model_admin.ld_content(
            ticket_admin_util.obj)
        mock_content.assert_called_once_with(words=12)

    def test_ld_source_without_source(self, ticket_admin_util):
        ticket_admin_util.obj.source = None
        result = ticket_admin_util.model_admin.ld_source(ticket_admin_util.obj)
        assert result == ''

    def test_ld_source_with_source(self, ticket_admin_util):
        source = Mock(spec=Source, icon='icon', title='title')
        ticket_admin_util.obj.source = source
        result = ticket_admin_util.model_admin.ld_source(ticket_admin_util.obj)
        assert source.title in result
        assert source.icon in result

    def test_ld_status_return_heldesk_status(self, ticket_admin_util):
        fake_status = 'open'
        ticket_admin_util.obj.status = fake_status
        with patch('helpdesk.admin.helpdesk_tags.helpdesk_status',
                   return_value=fake_status) as mock_ht:
            result = ticket_admin_util.model_admin.ld_status(
                ticket_admin_util.obj)
        assert result == fake_status
        mock_ht.assert_called_once_with(fake_status)


@pytest.fixture
def report_util(model_admin_util):
    from helpdesk.models import HelpdeskUser

    class FakeDbField(object):
        name = None

    model_admin_util.model_admin = ReportAdmin(Report, AdminSite)
    model_admin_util.model_admin.message_user = Mock(name='message_user')
    model_admin_util.report = Mock(spec=Report,
                                   sender_id=None,
                                   recipient_id=None,
                                   action_on_ticket='close',
                                   ticket=Mock(spec_set=Ticket,
                                               requester=HelpdeskUser()))
    model_admin_util.db_field = FakeDbField()
    return model_admin_util


# noinspection PyShadowingNames
class TestReportAdmin(object):
    @patch('django.contrib.admin.ModelAdmin.save_model')
    def test_save_model_set_sender_field(self, mock_save_model, report_util):
        report_util.model_admin.save_model(
            report_util.request, report_util.report, report_util.form, False)
        assert report_util.report.sender == report_util.request.user

    @patch('django.contrib.admin.ModelAdmin.save_model')
    def test_save_model_set_recipient_field(self, mock_save_model,
                                            report_util):
        report_util.model_admin.save_model(
            report_util.request, report_util.report, report_util.form, False)
        assert (report_util.report.recipient ==
                report_util.report.ticket.requester)

    @patch('django.contrib.admin.ModelAdmin.save_model')
    def test_save_model_call_closing_if_action_is_close(
            self, mock_save_model, report_util):
        report_util.report.action_on_ticket = 'close'
        report_util.model_admin.save_model(
            report_util.request, report_util.report, report_util.form, False)
        report_util.report.ticket.closing.assert_called_once_with(
            report_util.request.user)

    @patch('django.contrib.admin.ModelAdmin.save_model')
    def test_save_model_call_put_on_pending_without_estimated_date(
            self, mock_save_model, report_util):
        report_util.report.action_on_ticket = 'put_on_pending'
        report_util.model_admin.save_model(
            report_util.request, report_util.report, report_util.form, False)
        report_util.report.ticket.put_on_pending.assert_called_once_with(
            report_util.request.user, estimated_end_date=None)

    @patch('django.contrib.admin.ModelAdmin.save_model')
    def test_save_model_call_put_on_pending_with_estimated_date(
            self, mock_save_model, report_util):
        estimated_date = '2014-09-10'
        request = report_util.post(
            '/fake/', {'estimated_end_pending_date': estimated_date})
        report_util.report.action_on_ticket = 'put_on_pending'
        report_util.model_admin.save_model(
            request, report_util.report, report_util.form, False)
        report_util.report.ticket.put_on_pending.assert_called_once_with(
            request.user, estimated_end_date=estimated_date)

    @patch('django.contrib.admin.ModelAdmin.save_model')
    def test_save_model_call_remove_from_pending_if_action_is_remove_from(
            self, mock_save_model, report_util):
        report_util.report.action_on_ticket = 'remove_from_pending'
        report_util.model_admin.save_model(
            report_util.request, report_util.report, report_util.form, False)
        ticket = report_util.report.ticket
        ticket.remove_from_pending.assert_called_once_with(
            report_util.request.user)

    @patch('helpdesk.admin.Ticket.get_actions_for_report',
           return_value=['foo'])
    @patch('django.contrib.admin.ModelAdmin.formfield_for_choice_field')
    def test_call_formfield_for_choice_field_for_action_on_ticket_fields(
            self, mock_formfield_for, mock_get_actions, report_util):
        ticket = report_util.report.ticket
        report_util.model_admin.helpdesk_ticket = ticket
        report_util.db_field.name = 'action_on_ticket'
        report_util.model_admin.formfield_for_choice_field(
            report_util.db_field, report_util.request)
        mock_get_actions.assert_called_once_with(ticket=ticket)
        mock_formfield_for.assert_called_once_with(report_util.db_field,
                                                   request=report_util.request,
                                                   **{'choices': ['foo']})

    def test_get_readonly_fields_with_obj_return_all_fields_except(
            self, report_util):
        """
        Test that get_readonly_fields return all fields except
        'visible_from_requester'.
        """
        fields = list(report_util.model_admin.fields)
        assert 'visible_from_requester' in fields
        result = report_util.model_admin.get_readonly_fields(
            report_util.request, obj=report_util.report)
        fields.remove('visible_from_requester')
        assert result == fields

    def test_get_readonly_fields_without_obj_return_empty_list(
            self, report_util):
        """
        Test that get_readonly_fields return all fields except
        'visible_from_requester'.
        """
        assert (
            report_util.model_admin.get_readonly_fields(report_util.request)
            == list())

    @patch('helpdesk.admin.messages', autospec=True)
    def test_check_access_with_request_without_ticket_param(
            self, mock_messages, report_util):
        response_redirect = HttpResponseRedirect('/admin/')

        with patch('helpdesk.admin.redirect',
                   return_value=response_redirect) as mock_redirect:
            # response = ReportAdmin._check_access(report_util.request,
            #                                      report_util.model_admin)
            response = report_util.model_admin._check_access(
                report_util.request)
        assert response == response_redirect
        assert report_util.model_admin.helpdesk_ticket is None
        mock_redirect.assert_called_once_with(
            'admin:helpdesk_ticket_changelist')
        mock_messages.error.assert_called_once_with(
            report_util.request, ANY)

    @patch('helpdesk.admin.Ticket.objects.get',
           side_effect=Ticket.DoesNotExist)
    @patch('helpdesk.admin.messages', autospec=True)
    def test_check_access_with_request_with_ticket_not_existing(
            self, mock_messages, mock_get, report_util):
        response_redirect = HttpResponseRedirect('/admin/')
        request = report_util.get('/fake/?ticket=999')

        with patch('helpdesk.admin.redirect',
                   return_value=response_redirect) as mock_redirect:
            response = report_util.model_admin._check_access(request)

        assert response == response_redirect
        assert report_util.model_admin.helpdesk_ticket is None
        mock_redirect.assert_called_once_with(
            'admin:helpdesk_ticket_changelist')
        mock_messages.error.assert_called_once_with(request, ANY)

    def test_check_access_set_helpdesk_ticket_attr_and_return_none(
            self, report_util):
        ticket = report_util.report.ticket
        ticket.pk = '5'
        request = report_util.get('/fake/?ticket={}'.format(ticket.pk))

        with patch('helpdesk.admin.Ticket.objects.get',
                   return_value=ticket) as mock_get:
            response = report_util.model_admin._check_access(request)

        mock_get.assert_called_once_with(id=ticket.pk)
        assert report_util.model_admin.helpdesk_ticket == ticket
        assert response is None

    def test_add_view_return_result_of_check_access_if_returned_not_none(
            self, report_util):
        """
        Test that add_view call _check_access method and if his returned value
        is not None, this value is returned by add_view.
        """
        check_access_returned = HttpResponseRedirect('/admin/')
        report_util.model_admin._check_access = Mock(
            return_value=check_access_returned)

        response = report_util.model_admin.add_view(report_util.request)

        report_util.model_admin._check_access.assert_called_once_with(
            report_util.request)
        assert response == check_access_returned

    @patch('helpdesk.admin.ReportAdmin._check_access', return_value=None)
    @patch('django.contrib.admin.ModelAdmin.add_view')
    def test_add_view_set_estimated_end_pending_date_into_context(
            self, mock_add_view, mock_check_access, report_util):
        """
        Test that add_view call set 'estimated_end_pending_date' variable into
        context.
        """
        estimated_date = '2014-09-10'
        data = {'estimated_end_pending_date': estimated_date}
        request = report_util.post('/fake/', data)
        response_form = HttpResponse('form')
        mock_add_view.return_value = response_form

        report_util.model_admin.add_view(request, form_url='')

        mock_add_view.assert_called_once_with(
            request, form_url='', extra_context=data)

    @patch('helpdesk.admin.ReportAdmin._check_access', return_value=None)
    @patch('django.contrib.admin.ModelAdmin.add_view')
    def test_add_view_return_http_response(
            self, mock_add_view, mock_check_access, report_util):
        """
        Test that add_view call return normal http response (with form)
        """
        estimated_date = '2014-09-10'
        request = report_util.post(
            '/fake/', {'estimated_end_pending_date': estimated_date})
        response_form = HttpResponse('form')
        mock_add_view.return_value = response_form

        response = report_util.model_admin.add_view(request, '')

        assert response == response_form

    @patch('helpdesk.admin.ReportAdmin._check_access', return_value=None)
    @patch('django.contrib.admin.ModelAdmin.add_view')
    def test_add_view_return_redirect_ticket_change_view(
            self, mock_add_view, mock_check_access, report_util):
        """
        Test that add_view redirect to Ticket change view if super.add_view
        if in turn redirect to an default Report admin view.
        """
        ticket = Mock(spec_set=Ticket, pk=5)
        report_util.model_admin.helpdesk_ticket = ticket
        estimated_date = '2014-09-10'
        request = report_util.post(
            '/fake/', {'estimated_end_pending_date': estimated_date})
        default_redirect = HttpResponseRedirect('/admin/report/changelist/')
        ticket_redirect = HttpResponseRedirect(
            '/admin/helpdesk/ticket/{}/'.format(ticket.pk))
        mock_add_view.return_value = default_redirect

        with patch('helpdesk.admin.redirect',
                   return_value=ticket_redirect) as mock_redirect:
            response = report_util.model_admin.add_view(request, '')

        assert response == ticket_redirect
        mock_redirect.assert_called_once_with(
            admin_urlname(Ticket._meta, 'change'), ticket.pk)

    @patch('helpdesk.admin.messages', autospec=True)
    @patch('django.contrib.admin.ModelAdmin.change_view')
    def test_change_view_redirect_to_changelist_view(
            self, mock_change_view, mock_messages, report_util):
        request = report_util.post('/fake', {})
        report_id = 5
        model_mock = Mock(spec_set=Report)
        model_mock.objects.filter.return_value.count.return_value = 0
        report_util.model_admin.model = model_mock
        http_redirect = HttpResponseRedirect('/admin/report/changelist/')

        with patch('helpdesk.admin.redirect',
                   return_value=http_redirect) as mock_redirect:
            result = report_util.model_admin.change_view(request, report_id)

        assert result == http_redirect
        mock_redirect.assert_called_once_with(admin_urlname(model_mock._meta,
                                                            'changelist'))
        report_util.model_admin.message_user.assert_called_once_with(
            request, ANY, level=mock_messages.ERROR)

    @patch('django.contrib.admin.ModelAdmin.change_view')
    def test_change_view_return_default_response(
            self, mock_change_view, report_util):
        request = report_util.post('/fake', {})
        report_id = 5
        model_mock = Mock(spec_set=Report)
        model_mock.objects.filter.return_value.count.return_value = 1
        report_util.model_admin.model = model_mock
        form_response = HttpResponse('form')
        mock_change_view.return_value = form_response

        result = report_util.model_admin.change_view(request, report_id)

        assert result == form_response
        mock_change_view.assert_called_once_with(request, report_id)


@pytest.fixture
def report_ticket_inline(model_admin_util):
    model_admin_util.inline_model_admin = ReportTicketInline(Ticket, AdminSite)
    return model_admin_util


@patch('helpdesk.models.HelpdeskUser.get_from_request')
class TestReportTicketInline(object):

    @patch('django.contrib.admin.TabularInline.get_queryset')
    def test_get_queryset_return_default_queryset_is_admin(
            self, mock_get_qs, mock_gfr, report_ticket_inline):
        request = report_ticket_inline.request
        report_ticket_inline.user.is_admin.return_value = True
        mock_gfr.return_value = report_ticket_inline.user
        mock_get_qs.return_value = report_ticket_inline.qs

        qs = report_ticket_inline.inline_model_admin.get_queryset(request)

        mock_gfr.assert_called_once_with(request)
        mock_get_qs.assert_called_once_with(request)
        report_ticket_inline.user.is_admin.assert_called_once_with()
        assert qs == report_ticket_inline.qs

    @patch('django.contrib.admin.TabularInline.get_queryset')
    def test_get_queryset_return_default_queryset_is_not_admin(
            self, mock_get_qs, mock_gfr, report_ticket_inline):
        request = report_ticket_inline.request
        report_ticket_inline.user.is_admin.return_value = False
        mock_gfr.return_value = report_ticket_inline.user
        default_qs = report_ticket_inline.qs
        default_qs.filter.return_value = [1, 2]
        mock_get_qs.return_value = default_qs

        qs = report_ticket_inline.inline_model_admin.get_queryset(request)

        mock_gfr.assert_called_once_with(request)
        mock_get_qs.assert_called_once_with(request)
        report_ticket_inline.user.is_admin.assert_called_once_with()
        default_qs.filter.assert_called_once_with(
            sender=report_ticket_inline.user)
        assert qs == [1, 2]

@patch('django.contrib.admin.ChoicesFieldListFilter.__init__')
def test_status_list_filter_init_set_title_attr(mock_init):
    from helpdesk.admin import StatusListFilter
    status_list_filter = StatusListFilter(1, foo='bar')
    assert status_list_filter.title == StatusListFilter.title
    mock_init.assert_called_once_with(1, foo='bar')

