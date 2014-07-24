# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy

from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.contenttypes.generic import GenericTabularInline
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

from mezzanine.core.admin import TabularDynamicInlineAdmin

from .forms import TicketAdminAutocompleteForm, ReportAdminAutocompleteForm
from .templatetags.helpdesk_tags import helpdesk_status
from .models import (
    Category, Tipology, Attachment, Ticket, HelpdeskUser, Message,
    Report, StatusChangesLog, Source)
from .views import OpenTicketView, ObjectToolsView


class TipologyInline(TabularDynamicInlineAdmin):
    extra = 3
    model = Tipology


class MessageInline(TabularDynamicInlineAdmin):
    model = Message
    fields = ('content', 'recipient',)


class ReportTicketInline(TabularDynamicInlineAdmin):
    model = Report
    fields = ('content', 'action_on_ticket', 'visible_from_requester')

    def get_queryset(self, request):
        """If request.user is operator return queryset filterd by sender."""
        user = HelpdeskUser.get_from_request(request)
        qs = super(ReportTicketInline, self).get_queryset(request)
        if user.is_admin():
            return qs
        return qs.filter(sender=user)


class AttachmentInline(TabularDynamicInlineAdmin, GenericTabularInline):
    model = Attachment


class CategoryAdmin(admin.ModelAdmin):
    inlines = [TipologyInline]
    list_display = ['title', 'admin_tipologies']
    search_fields = ['title']


class TipologyAdmin(admin.ModelAdmin):
    list_display = ['title', 'admin_category', 'admin_sites']
    list_filter = ['category']
    search_fields = ['title', 'category__title']


class StatusListFilter(admin.ChoicesFieldListFilter):
    title = _('Status')

    def __init__(self, *args, **kwargs):
        super(StatusListFilter, self).__init__(*args, **kwargs)
        self.title = StatusListFilter.title


class TicketAdmin(admin.ModelAdmin):
    actions = ['open_tickets']
    date_hierarchy = 'created'
    fieldsets = (
        (None, {
            'fields': ['tipologies', 'priority', 'related_tickets', 'content'],
        }),
    )
    filter_horizontal = ('tipologies',)
    form = TicketAdminAutocompleteForm
    inlines = [AttachmentInline, MessageInline]
    list_display = ['ld_id', 'ld_content', 'ld_created', 'ld_status',
                    'ld_source']
    list_filter = ['priority', ('status', StatusListFilter), 'tipologies']
    list_per_page = 25
    list_select_related = True
    radio_fields = {'priority': admin.HORIZONTAL}
    search_fields = ['content', 'requester__username',
                     'requester__first_name', 'requester__last_name',
                     'tipologies__title']

    operator_read_only_fields = ['content', 'tipologies', 'priority', 'status']
    operator_list_display = ['requester']
    operator_list_filter = ['requester', 'assignee', 'source']
    operator_actions = ['requester', 'assignee']

    def get_request_helpdeskuser(self, request):
        return HelpdeskUser.get_from_request(request)

    @staticmethod
    def get_object_tools(request, view_name, obj=None):
        """

        :param request: HttpRequest
        :param view_name:
        :param obj:
        :type obj: Ticket
        :return: :rtype: list
        """
        user = HelpdeskUser.get_from_request(request)
        object_tools = {'change': []}
        admin_prefix_url = 'admin:'
        if obj:
            admin_prefix_url += '%s_%s' % (obj._meta.app_label,
                                           getattr(obj._meta, 'model_name',
                                                   obj._meta.module_name))
        if user.is_operator() or user.is_admin():
            if view_name == 'change' and obj:
                if obj.is_new():
                    object_tools[view_name].append(
                        {'url': reverse('{}_open'.format(admin_prefix_url),
                                        kwargs={'pk': obj.pk}),
                         'text': ugettext('Open and assign to me'),
                         'id': 'open_and_assign_ticket'})
                elif obj.is_open() or obj.is_pending():
                    url = '{}?ticket={}'.format(
                        reverse(admin_urlname(Report._meta, 'add')), obj.pk)
                    object_tools[view_name].append({
                        'url': url,
                        'text': ugettext('Add report'),
                        'id': 'add_report_to_ticket'})
                    if obj.is_pending():
                        default_content = _('The range of pending is over.')
                        url += ('&action_on_ticket=remove_from_pending&'
                                'content={}'.format(urlquote(default_content)))
                        object_tools[view_name].append({
                            'url': url,
                            'text': ugettext('Remove from pending'),
                            'id': 'add_report_for_remove_from_pending'})
        try:
            return object_tools[view_name]
        except KeyError:
            return list()

    # list_display methods customized #########################################
    def ld_id(self, obj):
        return obj.id
    ld_id.short_description = _('Id')

    def ld_content(self, obj):
        return obj.get_clean_content(words=12)
    ld_content.short_description = _('Content')

    def ld_status(self, obj):
        return helpdesk_status(obj.status)
    ld_status.admin_order_field = 'status'
    ld_status.allow_tags = True
    ld_status.short_description = _('Status')

    def ld_source(self, obj):
        if not obj.source:
            return ''
        context = Context({'icon_name': obj.source.icon,
                           'source': obj.source.title})
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
    def get_inline_instances(self, request, obj=None):
        if obj:
            if obj.is_closed():
                return list()
        # return [inline(self.model, self.admin_site)
        #         for inline in self.inlines]
        return super(TicketAdmin, self).get_inline_instances(request, obj=obj)

    def get_list_display(self, request):
        """
        Return default list_display if request.user is a requester. Otherwise
        if request.user is a operator or an admin return default list_display
        with operator_list_display.
        """
        user = self.get_request_helpdeskuser(request)
        list_display = list(super(TicketAdmin, self).get_list_display(request))
        if user.is_operator() or user.is_admin():
            list_display += self.operator_list_display
        return list_display

    def get_list_filter(self, request):
        """
        Return default list_filter if request.user is a requester. Otherwise
        if request.user is a operator, an admin or return default
        list_filter with append more fields.
        """
        user = self.get_request_helpdeskuser(request)
        list_filter = list(super(TicketAdmin, self).get_list_filter(request))
        if user.is_operator() or user.is_admin():
            list_filter += self.operator_list_filter
        return list_filter

    def get_fieldsets(self, request, obj=None):
        """
        Return default fieldsets if request.user is a requester.
        Otherwise request.user is a operator, an admin or superuser, append
        'requester' field to fieldsets.
        """
        user = self.get_request_helpdeskuser(request)
        fieldset = tuple() if obj else deepcopy(
            super(TicketAdmin, self).get_fieldsets(request, obj=obj))
        if not obj and user.is_operator() or user.is_admin():
            fieldset[0][1]['fields'] = (['requester', 'source'] +
                                        fieldset[0][1]['fields'])
        return fieldset

    def get_formsets(self, request, obj=None):
        user = self.get_request_helpdeskuser(request)
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, MessageInline):
                # hide MessageInline in the add view or user not is
                # a requester
                if obj is None or not user.is_requester():
                    continue  # pragma: no cover
            yield inline.get_formset(request, obj)

    def get_queryset(self, request):
        """
        Return a filtered queryset by user that match with request.user if
        request.user is a requester. Otherwise if request.user is a operator,
        an admin or superuser, queryset returned is not filtered.
        """
        user = self.get_request_helpdeskuser(request)
        # compatibility for django 1.5 where "get_queryset" method is
        # called "queryset" instead
        f_get_queryset = getattr(
            super(TicketAdmin, self), 'get_queryset', None)
        if not f_get_queryset:  # pragma: no cover
            f_get_queryset = getattr(super(TicketAdmin, self), 'queryset')
        qs = f_get_queryset(request)
        if user.is_superuser or user.is_operator() or user.is_admin():
            return qs
        return qs.filter(requester=user)

    def get_urls(self):
        # getattr is for re-compatibility django 1.5
        admin_prefix_url = '%s_%s' % (self.opts.app_label,
                                      getattr(self.opts, 'model_name',
                                              self.opts.module_name))
        urls = super(TicketAdmin, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^open/(?P<pk>\d+)$',
                self.admin_site.admin_view(OpenTicketView.as_view()),
                name='{}_open'.format(admin_prefix_url)),
            url(r'^object_tools/$',
                self.admin_site.admin_view(ObjectToolsView.as_view()),
                name='{}_object_tools'.format(admin_prefix_url)),
        )
        return my_urls + urls

    def queryset(self, request):
        """
        Compatibility for django 1.5 where "get_queryset" method is
        called "queryset" instead
        """
        return self.get_queryset(request)  # pragma: no cover

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Message):
                instance.sender = request.user
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
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

    # ModelsAdmin views methods customized ####################################
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # get the ticket's messages only if is change form
        user = self.get_request_helpdeskuser(request)
        if object_id:
            msgs = user.get_messages_by_ticket(object_id)
            changelogs = StatusChangesLog.objects.filter(
                ticket_id=object_id).order_by('created')
            extra_context.update({'ticket_messages': msgs,
                                  'ticket_changelogs': changelogs,
                                  'helpdesk_user': user})
        return super(TicketAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)

    # ModelsAdmin actions #####################################################
    def open_tickets(self, request, queryset):
        success_msg = _('Tickets %(ticket_ids)s successfully opened'
                        ' and assigned.')
        error_msg = _('Errors occours: \n%(errors)s.')
        success_ids = []
        error_data = []
        user = self.get_request_helpdeskuser(request)
        if user.is_operator() or user.is_admin():
            for ticket in queryset.filter(status=Ticket.STATUS.new):
                try:
                    ticket.opening(user)
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
                        ['ticket {} [{}]'.format(id, exc)
                         for id, exc in error_data])},
                    level=messages.ERROR)
    open_tickets.short_description = _('Open e assign selected Tickets')

    def get_actions(self, request):
        user = self.get_request_helpdeskuser(request)
        if user.is_requester():
            return []
        return super(TicketAdmin, self).get_actions(request)


class ReportAdmin(admin.ModelAdmin):
    fields = ('ticket', 'content', 'visible_from_requester',
              'action_on_ticket')
    form = ReportAdminAutocompleteForm
    list_display = ['id', 'ticket', 'created', 'content',
                    'visible_from_requester', 'action_on_ticket', 'sender',
                    'recipient']
    list_filter = ['sender', 'recipient', 'action_on_ticket',
                   'visible_from_requester']
    list_per_page = 20
    radio_fields = {'action_on_ticket': admin.VERTICAL}
    search_fields = ['ticket__pk', 'ticket__content', 'content']
    helpdesk_ticket = None

    @staticmethod
    def _check_access(request, modeladmin):
        ticket_id = request.GET.get('ticket', None)
        error = None
        setattr(modeladmin, 'helpdesk_ticket', None)
        if not ticket_id:
            error = "ERROR MANCANZA TICKET ID"
        else:
            try:
                setattr(modeladmin, 'helpdesk_ticket', Ticket.objects.get(
                    id=ticket_id))
            except Ticket.DoesNotExist:
                error = "ERROR TICKET ID NO TICKET MATCH"
        if error:
            messages.error(request, error)
            return redirect(admin_urlname(Ticket._meta, 'changelist'))

    def get_readonly_fields(self, request, obj=None):
        if obj:
            fields = list(self.fields)
            return [f for f in fields if f != 'visible_from_requester']
        return super(ReportAdmin, self).get_readonly_fields(request, obj=obj)

    def change_view(self, request, object_id, *args, **kwargs):
        if not self.model.objects.filter(pk=object_id,
                                         sender=request.user).count():
            self.message_user(request,
                              _("You can not change report with"
                                " id {}".format(object_id)),
                              level=messages.ERROR)
            return redirect(admin_urlname(self.model._meta, 'changelist'))
        return super(ReportAdmin, self).change_view(
            request, object_id, *args, **kwargs)

    def add_view(self, request, form_url='', extra_context=None):
        result = ReportAdmin._check_access(request, self)
        extra_context = extra_context or {}
        estimated_end_pending_date = request.POST.get(
            'estimated_end_pending_date', None)
        if estimated_end_pending_date:
            extra_context.update(
                {'estimated_end_pending_date': estimated_end_pending_date})
        if not result:
            result = super(ReportAdmin, self).add_view(
                request, form_url=form_url, extra_context=extra_context)
            if issubclass(result.__class__, HttpResponseRedirectBase):
                result = redirect(admin_urlname(Ticket._meta, 'change'),
                                  request.GET.get('ticket'))
        return result

    def formfield_for_choice_field(self, db_field, request=None, **kwargs):
        if db_field.name == 'action_on_ticket':
            kwargs['choices'] = Ticket.get_action_for_report(
                ticket=self.helpdesk_ticket)
        return super(ReportAdmin, self).formfield_for_choice_field(
            db_field, request=request, **kwargs)

    @atomic
    def save_model(self, request, obj, form, change):
        if obj.sender is None:
            obj.sender = request.user
        if obj.recipient is None:
            obj.recipient = obj.ticket.requester
        super(ReportAdmin, self).save_model(request, obj, form, change)
        if obj.action_on_ticket == 'close':
            obj.ticket.closing(request.user)
        elif obj.action_on_ticket == 'put_on_pending':
            estimated_end_date = request.POST.get(
                'estimated_end_pending_date', '').strip()
            if len(estimated_end_date) == 0:
                estimated_end_date = None
            obj.ticket.put_on_pending(request.user,
                                      estimated_end_date=estimated_end_date)
        elif obj.action_on_ticket == 'remove_from_pending':
            obj.ticket.remove_from_pending(request.user)


class SourceAdmin(admin.ModelAdmin):
    actions = None
    filter_horizontal = ('sites',)
    list_display = ['code', 'title', 'ld_icon']

    def has_delete_permission(self, request, obj=None):
        from helpdesk.core import DEFAULT_SOURCES
        if obj and obj.code in [code for code, title in DEFAULT_SOURCES]:
            error_msg = _(
                " %(title)s is a system %(model)s and is not"
                " eliminated.") % {'title': obj.title,
                                   'model': obj._meta.verbose_name.lower()}
            self.message_user(request, error_msg)
            return False
        return super(SourceAdmin, self).has_delete_permission(request, obj=obj)

    def ld_icon(self, obj):
        return obj.icon
    ld_icon.short_description = _('Icon')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tipology, TipologyAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Source, SourceAdmin)
