# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy

from django.conf import urls as django_urls
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
from django import VERSION as DJANGO_VERSION

from mezzanine.core.admin import TabularDynamicInlineAdmin

from .forms import TicketAdminAutocompleteForm, ReportAdminAutocompleteForm
from .templatetags import helpdesk_tags
from .models import (
    Category, Tipology, Attachment, Ticket, HelpdeskUser, Message,
    Report, StatusChangesLog, Source, SiteConfiguration)
from .views import OpenTicketView, ObjectToolsView


DEFAULT_LIST_PER_PAGE = 15


class TipologyInline(TabularDynamicInlineAdmin):
    extra = 3
    model = Tipology


class MessageInline(TabularDynamicInlineAdmin):
    model = Message
    fields = ('content', )


class ReportTicketInline(TabularDynamicInlineAdmin):
    model = Report
    fields = ('content', 'action_on_ticket', 'visible_from_requester')

    def get_queryset(self, request):
        """If request.user is operator return queryset filterd by sender."""
        user = HelpdeskUser.get_from_request(request)
        # re-compatibility for django 1.5 where "get_queryset" method is
        # called "queryset" instead
        _super = super(ReportTicketInline, self)
        qs = (getattr(_super, 'get_queryset', None)
              or getattr(_super, 'queryset'))(request)
        if user.is_admin():
            return qs
        return qs.filter(sender=user)


class AttachmentInline(TabularDynamicInlineAdmin, GenericTabularInline):
    model = Attachment


class CategoryAdmin(admin.ModelAdmin):
    inlines = [TipologyInline]
    list_display = ['title', 'admin_tipologies']
    list_per_page = DEFAULT_LIST_PER_PAGE
    search_fields = ['title']


# noinspection PyMethodMayBeStatic
class TipologyAdmin(admin.ModelAdmin):
    fields = ('title', 'category', 'priority', 'sites',)
    filter_horizontal = ('sites',)
    list_display = ['title', 'ld_category', 'ld_sites']
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


class StatusListFilter(admin.ChoicesFieldListFilter):
    title = _('Status')

    def __init__(self, *args, **kwargs):
        super(StatusListFilter, self).__init__(*args, **kwargs)
        self.title = StatusListFilter.title


class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site', 'email_addrs_to', 'email_addr_from']
    list_per_page = DEFAULT_LIST_PER_PAGE


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
    form = TicketAdminAutocompleteForm
    inlines = [AttachmentInline]
    list_display = ['ld_id', 'ld_content', 'ld_created', 'ld_status',
                    'ld_source', 'ld_assegnee']
    list_filter = ['priority', ('status', StatusListFilter), 'tipologies']
    list_per_page = DEFAULT_LIST_PER_PAGE
    list_select_related = True
    radio_fields = {'priority': admin.HORIZONTAL}
    search_fields = ['content', 'requester__username',
                     'requester__first_name', 'requester__last_name',
                     'tipologies__title', 'tipologies__category__title']

    operator_read_only_fields = ['content', 'tipologies', 'priority', 'status']
    operator_list_display = ['requester']
    operator_list_filter = ['requester', 'assignee', 'source']
    operator_actions = ['requester', 'assignee']

    def get_request_helpdeskuser(self, request):
        return HelpdeskUser.get_from_request(request)

    def get_search_fields_info(self, request):
        return _('content of ticket, title of tipology, title of category'
                 ' ,username, last name, first name of requester')

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
                        'text': ugettext('Add Report'),
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
        return obj.pk
    ld_id.admin_order_field = 'id'
    ld_id.short_description = _('Id')

    def ld_content(self, obj):
        return obj.get_clean_content(words=12)
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
        user = self.get_request_helpdeskuser(request)
        fieldset = tuple() if obj else deepcopy(
            super(TicketAdmin, self).get_fieldsets(request, obj=obj))
        if not obj and user.is_requester():
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
            user = self.get_request_helpdeskuser(request)
            if user.is_requester():
                return ([MessageInline(self.model, self.admin_site)]
                        + default_inlines_instances)
        return default_inlines_instances

    def get_list_display(self, request):
        """
        Return default list_display if request.user is a requester. Otherwise
        if request.user is a operator or an admin return default list_display
        with operator_list_display.
        """
        user = HelpdeskUser.get_from_request(request)
        list_display = list(super(TicketAdmin, self).get_list_display(request))
        if user.is_operator() or user.is_admin():
            list_display = (list_display[:1] + self.operator_list_display +
                            list_display[1:])
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

    def get_queryset(self, request):
        """
        Return a filtered queryset by user that match with request.user if
        request.user is a requester. Otherwise if request.user is a operator,
        an admin or superuser, queryset returned is not filtered.
        """
        user = self.get_request_helpdeskuser(request)
        # re-compatibility for django 1.5 where "get_queryset" method is
        # called "queryset" instead
        _super = super(TicketAdmin, self)
        qs = (getattr(_super, 'get_queryset', None)
              or getattr(_super, 'queryset'))(request)
        if user.is_superuser or user.is_operator() or user.is_admin():
            return qs
        return qs.filter(requester=user)

    def get_urls(self):
        # getattr is for re-compatibility django 1.5
        admin_prefix_url = '%s_%s' % (self.opts.app_label,
                                      getattr(self.opts, 'model_name',
                                              self.opts.module_name))
        urls = super(TicketAdmin, self).get_urls()
        my_urls = django_urls.patterns(
            '',
            django_urls.url(
                r'^open/(?P<pk>\d+)/$',
                self.admin_site.admin_view(OpenTicketView.as_view()),
                name='{}_open'.format(admin_prefix_url)),
            django_urls.url(
                r'^object_tools/$',
                self.admin_site.admin_view(ObjectToolsView.as_view()),
                name='{}_object_tools'.format(admin_prefix_url)),
        )
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
        return super(TicketAdmin, self).changelist_view(
            request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # get the ticket's messages only if is change form
        user = self.get_request_helpdeskuser(request)
        msgs = user.get_messages_by_ticket(object_id)
        changelogs = StatusChangesLog.objects.filter(
            ticket_id=object_id).order_by('created')
        extra_context.update({'ticket_messages': msgs,
                              'ticket_changelogs': changelogs,
                              'helpdesk_user': user})
        return super(TicketAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)

    # ModelsAdmin actions #####################################################
    def get_actions(self, request):
        user = self.get_request_helpdeskuser(request)
        if user.is_requester():
            return list()
        return super(TicketAdmin, self).get_actions(request)

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
                        ['ticket {} [{}]'.format(pk, exc)
                         for pk, exc in error_data])},
                    level=messages.ERROR)
    open_tickets.short_description = _('Open e assign selected Tickets')


class ReportAdmin(admin.ModelAdmin):
    fields = ('ticket', 'content', 'visible_from_requester',
              'action_on_ticket')
    form = ReportAdminAutocompleteForm
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


# statements for supporting django version < 1.6
if DJANGO_VERSION[0] == 1 and DJANGO_VERSION[1] < 6:
    ReportTicketInline.queryset = ReportTicketInline.get_queryset
    TicketAdmin.queryset = TicketAdmin.get_queryset


class HeldeskUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(HelpdeskUser, HeldeskUserAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(SiteConfiguration, SiteConfigurationAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Tipology, TipologyAdmin)
