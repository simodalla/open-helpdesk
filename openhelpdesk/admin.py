# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import waffle

from copy import deepcopy

from django.conf import urls as django_urls
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import Group
try:
    from django.contrib.contenttypes.generic import GenericTabularInline
except ImportError:
    from django.contrib.contenttypes.admin import GenericTabularInline
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
try:
    from django.db.transaction import atomic
except ImportError:  # pragma: no cover
    from django.db.transaction import commit_on_success as atomic
from django.utils.http import urlquote
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import redirect
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _, ugettext
from django import VERSION as DJANGO_VERSION

from mezzanine.conf import settings
from mezzanine.core.admin import (TabularDynamicInlineAdmin,
                                  StackedDynamicInlineAdmin)

from . import forms
from . import filters
from .templatetags import helpdesk_tags
from .models import (
    Category, Tipology, Attachment, Ticket, Message,
    Report, StatusChangesLog, Source, SiteConfiguration, OrganizationSetting,
    Subteam, TeammateSetting)
from .core import HelpdeskUser
from .views import OpenTicketView, ObjectToolsView


DEFAULT_LIST_PER_PAGE = 15


class TipologyInline(StackedDynamicInlineAdmin):
    model = Tipology
    fields = ('title', 'sites', 'enable_on_organizations',
              'disable_on_organizations')
    filter_horizontal = ('sites', 'enable_on_organizations',
                         'disable_on_organizations')


class MessageInline(TabularDynamicInlineAdmin):
    model = Message
    fields = ('content', )


class ReportTicketInline(TabularDynamicInlineAdmin):
    model = Report
    fields = ('content', 'action_on_ticket', 'visible_from_requester')

    def get_queryset(self, request):
        """If request.user is operator return queryset filterd by sender."""
        hu = HelpdeskUser(request)
        qs = super(ReportTicketInline, self).get_queryset(request)
        if hu.is_admin():
            return qs
        return qs.filter(sender=hu.user)


class AttachmentInline(TabularDynamicInlineAdmin, GenericTabularInline):
    model = Attachment


class CategoryAdmin(admin.ModelAdmin):
    form = forms.CategoryAdminAutocompleteForm
    inlines = [TipologyInline]
    list_display = ['title',
                    'admin_tipologies',
                    'admin_enable_on_organizations']
    list_per_page = DEFAULT_LIST_PER_PAGE
    list_select_related = True
    search_fields = ['title', 'organizations']


# noinspection PyMethodMayBeStatic
class TipologyAdmin(admin.ModelAdmin):
    fields = ('title', 'category', 'sites', 'enable_on_organizations',
              'disable_on_organizations')
    form = forms.TipologyAdminAutocompleteForm
    list_display = ['title', 'ld_category', 'ld_sites',
                    'admin_enable_on_organizations',
                    'admin_disable_on_organizations']
    list_filter = ['category']
    list_per_page = DEFAULT_LIST_PER_PAGE
    list_select_related = True
    search_fields = ['title', 'category__title']

    def ld_category(self, obj):
        return (
            '<a href="{url}?id={category.pk}" class="view_category">'
            '{category.title}</a>'.format(
                url=reverse(admin_urlname(obj.category._meta, 'changelist')),
                category=obj.category))
    ld_category.allow_tags = True
    ld_category.admin_order_field = 'category'
    ld_category.short_description = _('Category')

    def ld_sites(self, obj):
        return '<br>'.join(
            ['<a href="{url}?id={site.pk}" class="view_site">{site.domain}'
             '</a>'.format(url=reverse(admin_urlname(s._meta, 'changelist')),
                           site=s)
             for s in obj.sites.all()])
    ld_sites.allow_tags = True
    ld_sites.short_description = _('Enabled on Sites')


class OrganizationSettingAdmin(admin.ModelAdmin):
    list_display = ['title', 'email_domain', 'active',
                    'filter_label', 'email_background_color']
    list_editable = ['active', 'filter_label', 'email_background_color']


class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site', 'ld_emails', 'ld_admins', 'ld_operators',
                    'ld_requesters']
    list_per_page = DEFAULT_LIST_PER_PAGE
    search_fields = ['site__sitepermission__user__username']

    @staticmethod
    def format_usernames_by_group(obj, group):
        return ', '.join(sorted(obj.get_usernames_by_group(group)))

    def ld_requesters(self, obj):
        return self.format_usernames_by_group(
            obj, settings.HELPDESK_REQUESTERS)
    ld_requesters.allow_tags = True
    ld_requesters.short_description = _('Requesters')

    def ld_operators(self, obj):
        return self.format_usernames_by_group(obj, settings.HELPDESK_OPERATORS)
    ld_operators.allow_tags = True
    ld_operators.short_description = _('Operators')

    def ld_admins(self, obj):
        return self.format_usernames_by_group(obj, settings.HELPDESK_ADMINS)
    ld_admins.allow_tags = True
    ld_admins.short_description = _('Admins')

    def ld_emails(self, obj):
        result = (['(from) {}'.format(obj.email_addr_from)] +
                  ['(to) {}'.format(email) for email in obj.email_addrs_to])
        return '<hr>'.join(result)
    ld_emails.allow_tags = True
    ld_emails.short_description = _('Emails')
    

# noinspection PyProtectedMember
class TicketAdmin(admin.ModelAdmin):
    actions = ['open_tickets']
    date_hierarchy = 'created'
    fieldsets = (
        (None, {
            'fields': ['requester', 'source', 'tipologies', 'priority',
                       'related_tickets', 'content'],
        }),
    )
    filter_vertical = ('tipologies',)
    form = forms.TicketAdminAutocompleteForm
    inlines = [AttachmentInline]
    list_display = ['ld_id', 'ld_content', 'ld_created', 'ld_status',
                    # 'ld_source', 'ld_assegnee']
                    'priority', 'ld_assegnee']
    list_filter = ['priority',
                   ('status', filters.StatusListFilter),
                   'tipologies']
    list_max_show_all = 50
    list_per_page = DEFAULT_LIST_PER_PAGE
    list_select_related = True
    radio_fields = {'priority': admin.HORIZONTAL}
    search_fields = ['content', 'requester__username', 'requester__email',
                     'requester__first_name', 'requester__last_name',
                     'tipologies__title', 'tipologies__category__title']

    operator_read_only_fields = ['content', 'tipologies', 'priority', 'status']
    operator_list_display = ['ld_requester', 'ld_organization']
    operator_list_filter = [filters.SubteamFilter,
                            filters.EmailDomainFilter,
                            ('assignee', admin.RelatedOnlyFieldListFilter),
                            'source']
    operator_actions = ['requester', 'assignee']

    def get_request_helpdeskuser(self, request):
        return HelpdeskUser(request)

    def get_search_fields_info(self, request):
        return _('content of ticket, title of tipology, title of category'
                 ' ,username, last name, first name, email of requester')

    @staticmethod
    def get_object_tools(request, view_name, obj=None):
        """

        :param request: HttpRequest
        :param view_name:
        :param obj:
        :type obj: Ticket
        :return: :rtype: list
        """
        hu = HelpdeskUser(request)
        object_tools = {'change': []}
        admin_prefix_url = 'admin:'
        if obj:
            admin_prefix_url += '%s_%s' % (obj._meta.app_label,
                                           obj._meta.model_name)
        if hu.is_operator() or hu.is_admin():
            if view_name == 'change' and obj:
                if obj.is_new():
                    object_tools[view_name].append(
                        {'url': reverse('{}_open'.format(admin_prefix_url),
                                        kwargs={'pk': obj.pk}),
                         'text': ugettext('Open and assign to me'),
                         'id': 'open_and_assign_ticket',
                         'awesome_image': 'hand-o-up'})
                elif obj.is_open() or obj.is_pending():
                    url = '{}?ticket={}'.format(
                        reverse(admin_urlname(Report._meta, 'add')), obj.pk)
                    object_tools[view_name].append({
                        'url': url,
                        'text': ugettext('Add Report'),
                        'id': 'add_report_to_ticket',
                        'awesome_image': 'cogs'})
                    if obj.is_pending():
                        default_content = _('The range of pending is over.')
                        url += ('&action_on_ticket=remove_from_pending&'
                                'content={}'.format(urlquote(default_content)))
                        object_tools[view_name].append({
                            'url': url,
                            'text': ugettext('Remove from pending'),
                            'id': 'add_report_for_remove_from_pending',
                            'awesome_image': 'clock-o'})
        try:
            return object_tools[view_name]
        except KeyError:
            return list()

    # list_display methods customized #########################################
    def ld_id(self, obj):
        return obj.pk
    ld_id.admin_order_field = 'id'
    ld_id.short_description = _('Id')

    def ld_requester(self, obj):
        return obj.requester.username
    ld_requester.admin_order_field = 'requester'
    ld_requester.allow_tags = True
    ld_requester.short_description = _('Requester')

    def ld_organization(self, obj):
        try:
            return OrganizationSetting.email_objects.get_field(
                obj.requester.email, 'title').strip()
        except (ValidationError, OrganizationSetting.DoesNotExist):
            return '<a href="{}">{}</a>'.format(
                reverse('admin:auth_user_change', args=(obj.requester.pk,)),
                _("Please, verify email address"))
    ld_organization.allow_tags = True
    ld_organization.short_description = _('Organization')

    def ld_content(self, obj):
        return obj.get_clean_content(words=18)
    ld_content.short_description = _('Content')

    def ld_status(self, obj):
        return helpdesk_tags.helpdesk_status(obj.status)
    ld_status.admin_order_field = 'status'
    ld_status.allow_tags = True
    ld_status.short_description = _('Status')

    def ld_assegnee(self, obj):
        return obj.assignee or _('Not assigned')
    ld_assegnee.admin_order_field = 'assignee'
    ld_assegnee.short_description = _('Assignee')

    def ld_source(self, obj):
        if not obj.source:
            return ''
        context = Context({'icon_name': obj.source.icon,
                           'source': _(obj.source.title)})
        return Template("{% load helpdesk_tags %}"
                        "{% awesome_icon icon_name %}"
                        "&nbsp;&nbsp;{{ source }}").render(context)
    ld_source.admin_order_field = 'source'
    ld_source.allow_tags = True
    ld_source.short_description = _('Source')

    def ld_created(self, obj):
        from django.template import defaultfilters
        return defaultfilters.date(obj.created, 'SHORT_DATETIME_FORMAT')
    ld_created.admin_order_field = 'created'
    ld_created.allow_tags = True
    ld_created.short_description = _('Created')

    # ModelsAdmin methods customized ##########################################
    def get_fieldsets(self, request, obj=None):
        """
        Return default fieldsets if request.user is a requester.
        Otherwise request.user is a operator, an admin or superuser, append
        'requester' field to fieldsets.
        """
        hu = self.get_request_helpdeskuser(request)
        fieldset = tuple() if obj else deepcopy(
            super(TicketAdmin, self).get_fieldsets(request, obj=obj))
        if not obj and hu.is_requester():
            [fieldset[0][1]['fields'].remove(field)
             for field in ['requester', 'source']
             if field in fieldset[0][1]['fields']]
        return fieldset

    def get_inline_instances(self, request, obj=None):
        if obj and obj.is_closed():
            return list()
        default_inlines_instances = [inline(self.model, self.admin_site)
                                     for inline in self.inlines]
        if obj:
            hu = self.get_request_helpdeskuser(request)
            if hu.is_requester():
                return ([MessageInline(self.model, self.admin_site)]
                        + default_inlines_instances)
        return default_inlines_instances

    def get_list_display(self, request):
        """
        Return default list_display if request.user is a requester. Otherwise
        if request.user is a operator or an admin return default list_display
        with operator_list_display.
        """
        hu = HelpdeskUser(request)
        list_display = list(super(TicketAdmin, self).get_list_display(request))
        if hu.is_operator() or hu.is_admin():
            list_display = (list_display[:1] + self.operator_list_display +
                            list_display[1:])
        return list_display

    def get_list_filter(self, request):
        """
        Return default list_filter if request.user is a requester. Otherwise
        if request.user is a operator, an admin or return default
        list_filter with append more fields.
        """
        hu = self.get_request_helpdeskuser(request)
        list_filter = list(super(TicketAdmin, self).get_list_filter(request))
        if hu.is_operator() or hu.is_admin():
            list_filter += self.operator_list_filter
        return list_filter

    def get_queryset(self, request):
        """
        Return a filtered queryset by user that match with request.user if
        request.user is a requester. Otherwise if request.user is a operator,
        an admin or superuser, queryset returned is not filtered.
        """
        hu = self.get_request_helpdeskuser(request)
        qs = super(TicketAdmin, self).get_queryset(request)
        if hu.user.is_superuser or hu.is_operator() or hu.is_admin():
            return qs
        return qs.filter(requester=hu.user)

    def get_changeform_initial_data(self, request):
        """
        This method is an hook for filter the tipologies for an requester user.
        """
        hu = HelpdeskUser(request)
        initial = super(TicketAdmin, self).get_changeform_initial_data(request)
        if hu.is_requester():
            try:
                tipology_pks = OrganizationSetting.email_objects.get_tipologies(
                    request.user.email).values_list('pk', flat=True)
                initial.update({'__tipology_pks': tipology_pks})
            except Exception as e:
                raise e
        return initial

    def get_urls(self):
        # getattr is for re-compatibility django 1.5
        admin_prefix_url = '%s_%s' % (self.opts.app_label,
                                      self.opts.model_name)
        urls = super(TicketAdmin, self).get_urls()
        my_urls = [
            django_urls.url(
                r'^open/(?P<pk>\d+)/$',
                self.admin_site.admin_view(OpenTicketView.as_view()),
                name='{}_open'.format(admin_prefix_url)),
            django_urls.url(
                r'^object_tools/$',
                self.admin_site.admin_view(ObjectToolsView.as_view()),
                name='{}_object_tools'.format(admin_prefix_url)),
        ]
        return my_urls + urls

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Message):
                if instance.sender_id is None:
                    instance.sender = request.user
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        """
        :param obj: Ticket object
        :type obj: openhelpdesk.models.Ticket
        """
        if obj.source_id is None:
            try:
                obj.source = Source.get_default_obj()
            except Source.DoesNotExist:
                pass
        if obj.requester_id is None:
            obj.requester = request.user
        if obj:
            obj.insert_by = request.user
        super(TicketAdmin, self).save_model(request, obj, form, change)
        if not change:
            obj.initialize()

    def save_related(self, request, form, formsets, change):
        """
        Save related is called after "save_model" method where related objects
        aren't saved yet. Here super.save_related is called, it's save all
        related object and only after send_email_to_operators_on_adding is
        called on Ticket objets because in this method are used the related
        objects (eg: ticket.tipologies.all)
        """
        super(TicketAdmin, self).save_related(request, form, formsets, change)
        obj = form.instance
        """:type : openhelpdesk.models.Ticket"""
        if not change and obj.requester_id == obj.insert_by_id:
            obj.send_email_to_operators_on_adding(request)

    # ModelsAdmin views methods customized ####################################

    def changelist_view(self, request, extra_context=None):
        hp = HelpdeskUser(request)

        if hp.is_requester():
            try:
                del request.session['oh_query_string']
                del request.session['oh_proxied']
            except KeyError:
                pass
            return super(TicketAdmin, self).changelist_view(
                request, extra_context=extra_context)

        filter_clean = False
        if 'filter_clean' in request.GET:
            request.GET = request.GET.copy()
            filter_clean = True
            del request.GET['filter_clean']

        proxied = request.session.get('oh_proxied', False)

        if not proxied:
            if hp.is_operator() or hp.is_admin():
                session_query_string = request.session.get(
                    'oh_query_string', '')
                if not session_query_string:
                    try:
                        subteam = hp.user.oh_teammate.default_subteam
                    except TeammateSetting.DoesNotExist:
                        subteam = None
                    if subteam:
                        query_string = 'subteam={}'.format(subteam)
                        request.session['oh_query_string'] = query_string
                        request.session['oh_proxied'] = True
                        url = '{}?{}'.format(
                            reverse(admin_urlname(self.model._meta,
                                                  'changelist')),
                            query_string)
                        return redirect(url)
                else:
                    query_string = request.META.get('QUERY_STRING', '')
                    if query_string:
                        request.session['oh_query_string'] = query_string
                    else:
                        request.session['oh_proxied'] = True
                        url = '{}?{}'.format(
                            reverse(admin_urlname(self.model._meta,
                                                  'changelist')),
                            session_query_string)
                        return redirect(url)
            else:
                try:
                    del request.session['oh_query_string']
                except KeyError:
                    pass
        request.session['oh_proxied'] = False
        return super(TicketAdmin, self).changelist_view(
            request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        try:
            os = OrganizationSetting.email_objects.get(request.user.email)
            extra_context = extra_context or {}
            extra_context['organization_setting'] = os
        except (ValidationError, OrganizationSetting.DoesNotExist) as e:
            msg = _('Sorry! Your email address is invalid. '
                    'Contact the support service for fix this.')
            messages.error(request, _(msg))
            # TODO inserire un ticket in maniera automatica
            return redirect(admin_urlname(self.model._meta, 'changelist'))
        return super(TicketAdmin, self).add_view(request, form_url=form_url,
                                                 extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # get the ticket's messages only if is change form
        hu = self.get_request_helpdeskuser(request)
        msgs = hu.get_messages_by_ticket(object_id)
        changelogs = StatusChangesLog.objects.filter(
            ticket_id=object_id).order_by('created')
        extra_context.update({'ticket_messages': msgs,
                              'ticket_changelogs': changelogs,
                              'helpdesk_user': hu.user})
        return super(TicketAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)

    # ModelsAdmin actions #####################################################
    def get_actions(self, request):
        hu = self.get_request_helpdeskuser(request)
        if hu.is_requester():
            return list()
        return super(TicketAdmin, self).get_actions(request)

    def open_tickets(self, request, queryset):
        success_msg = _('Tickets %(ticket_ids)s successfully opened'
                        ' and assigned.')
        error_msg = _('Errors occours: \n%(errors)s.')
        success_ids = []
        error_data = []
        hu = self.get_request_helpdeskuser(request)
        if hu.is_operator() or hu.is_admin():
            for ticket in queryset.filter(status=Ticket.STATUS.new):
                try:
                    ticket.opening(hu.user)
                    success_ids.append(str(ticket.pk))
                except Exception as e:
                    error_data.append((ticket.pk, str(e)))
            if success_ids:
                self.message_user(
                    request,
                    success_msg % {'ticket_ids': ','.join(success_ids)},
                    level=messages.SUCCESS)
            if error_data:
                self.message_user(
                    request,
                    error_msg % {'errors': ', '.join(
                        ['ticket {} [{}]'.format(pk, exc)
                         for pk, exc in error_data])},
                    level=messages.ERROR)
    open_tickets.short_description = _('Open e assign selected Tickets')


class ReportAdmin(admin.ModelAdmin):
    fields = ('ticket', 'content', 'visible_from_requester',
              'action_on_ticket')
    form = forms.ReportAdminForm
    list_display = ['id', 'ticket', 'created', 'content',
                    'visible_from_requester', 'action_on_ticket', 'sender',
                    'recipient']
    list_filter = ['sender', 'recipient', 'action_on_ticket',
                   'visible_from_requester']
    list_per_page = DEFAULT_LIST_PER_PAGE
    list_select_related = True
    radio_fields = {'action_on_ticket': admin.VERTICAL}
    search_fields = ['ticket__pk', 'ticket__content', 'content']
    helpdesk_ticket = None

    def _check_access(self, request):
        ticket_id = request.GET.get('ticket', None)
        error = False
        setattr(self, 'helpdesk_ticket', None)
        if not ticket_id:
            error = True
        else:
            try:
                setattr(self, 'helpdesk_ticket', Ticket.objects.get(
                    id=ticket_id))
            except Ticket.DoesNotExist:
                error = True
        if error:
            error = _("Error: wrong request for adding Report.")
            messages.error(request, error)
            return redirect(admin_urlname(Ticket._meta, 'changelist'))

    def get_readonly_fields(self, request, obj=None):
        """
        If obj not is None (we are in change vien) is possible updatading only
        'visible_from_requester' field.
        """
        if obj:
            fields = list(self.fields)
            return [f for f in fields if f != 'visible_from_requester']
        return list()

    def change_view(self, request, object_id, *args, **kwargs):
        """
        If request.user try to change an Report which sender field is not the
        same, request.user is redirect to Report changelist view.
        """
        if not self.model.objects.filter(pk=object_id,
                                         sender=request.user).count():
            self.message_user(request,
                              _("You can not change Report with id"
                                " %(report_id)s") % {'report_id': object_id},
                              level=messages.ERROR)
            return redirect(admin_urlname(self.model._meta, 'changelist'))
        return super(ReportAdmin, self).change_view(
            request, object_id, *args, **kwargs)

    def add_view(self, request, form_url='', extra_context=None):
        result = self._check_access(request)
        if result is not None:
            return result
        extra_context = extra_context or {}
        estimated_end_pending_date = request.POST.get(
            'estimated_end_pending_date', '').strip()
        if estimated_end_pending_date:
            extra_context.update(
                {'estimated_end_pending_date': estimated_end_pending_date})
        result = super(ReportAdmin, self).add_view(
            request, form_url=form_url, extra_context=extra_context)
        if issubclass(result.__class__, HttpResponseRedirectBase):
            result = redirect(admin_urlname(Ticket._meta, 'change'),
                              self.helpdesk_ticket.pk)
        return result

    def formfield_for_choice_field(self, db_field, request=None, **kwargs):
        if db_field.name == 'action_on_ticket':
            kwargs['choices'] = Ticket.get_actions_for_report(
                ticket=self.helpdesk_ticket)
        return super(ReportAdmin, self).formfield_for_choice_field(
            db_field, request=request, **kwargs)

    @atomic
    def save_model(self, request, obj, form, change):
        cached_obj = self.model.objects.get(pk=obj.pk) if change else None
        if obj.sender_id is None:
            obj.sender = request.user
        if obj.recipient_id is None:
            obj.recipient = obj.ticket.requester
        super(ReportAdmin, self).save_model(request, obj, form, change)
        if obj.action_on_ticket == 'close':
            obj.ticket.closing(request.user)
        elif obj.action_on_ticket == 'put_on_pending':
            estimated_end_date = request.POST.get(
                'estimated_end_pending_date', '').strip() or None
            obj.ticket.put_on_pending(request.user,
                                      estimated_end_date=estimated_end_date)
        elif obj.action_on_ticket == 'remove_from_pending':
            obj.ticket.remove_from_pending(request.user)
        # send notification
        if waffle.switch_is_active('openhelpdesk_notify_to_requester'):
            self.notify_to_requester(request, obj, cached_obj=cached_obj,
                                     change=cached_obj)

    def notify_to_requester(self, request, obj, cached_obj=None,
                            change=False, method='email'):
        if method not in ['email']:
            raise TypeError('Method for notification "{}" not'
                            ' available'.format(method))
        notify = False
        if obj.visible_from_requester:
            if not change:
                # notify if report is added and field visible_from_requester
                # is True
                notify = True
            else:
                if cached_obj and not cached_obj.visible_from_requester:
                    # notify if report before the saving are not
                    # visible_from_requester and after saving is
                    # visible_from_requester
                    notify = True
        if notify and method == 'email':
            obj.send_email_to_requester(request)


class SourceAdmin(admin.ModelAdmin):
    actions = None
    filter_horizontal = ('sites',)
    list_display = ['code', 'title', 'ld_icon']
    list_per_page = DEFAULT_LIST_PER_PAGE

    def has_delete_permission(self, request, obj=None):
        from openhelpdesk.core import DEFAULT_SOURCES
        if obj and obj.code in [source[0] for source in DEFAULT_SOURCES]:
            error_msg = _(
                "%(title)s is a system %(model)s and is not"
                " eliminated.") % {'title': obj.title,
                                   'model': obj._meta.verbose_name.lower()}
            self.message_user(request, error_msg, level=messages.ERROR)
            return False
        return super(SourceAdmin, self).has_delete_permission(request, obj=obj)

    def ld_icon(self, obj):
        return obj.icon
    ld_icon.short_description = _('Icon')


class SubteamAdmin(admin.ModelAdmin):
    form = forms.SubteamAdminAutocompleteForm
    list_display = ['title', ]
    list_per_page = DEFAULT_LIST_PER_PAGE


class TeammateSettingAdmin(admin.ModelAdmin):
    form = forms.TeammateSettingAdminAutocompleteForm
    list_display = ['user', 'default_subteam']
    list_per_page = DEFAULT_LIST_PER_PAGE


admin.site.register(Category, CategoryAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(SiteConfiguration, SiteConfigurationAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Tipology, TipologyAdmin)
admin.site.register(OrganizationSetting, OrganizationSettingAdmin)
admin.site.register(Subteam, SubteamAdmin)
admin.site.register(TeammateSetting, TeammateSettingAdmin)

