# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.admin import TabularDynamicInlineAdmin, OwnableAdmin

from .models import Category, Tipology, Attachment, Ticket, HelpdeskUser


class TipologyInline(TabularDynamicInlineAdmin):
    extra = 3
    model = Tipology


class AttachmentInline(TabularDynamicInlineAdmin):
    extra = 1
    model = Attachment


class CategoryAdmin(admin.ModelAdmin):
    inlines = [TipologyInline]
    list_display = ['title', 'admin_tipologies']
    search_fields = ['title']


class TipologyAdmin(admin.ModelAdmin):
    list_display = ['title', 'admin_category', 'admin_sites']
    list_filter = ['category']
    search_fields = ['title', 'category__title']


class TicketAdmin(admin.ModelAdmin):
    filter_horizontal = ('tipologies', 'related_tickets')
    inlines = [AttachmentInline]
    list_display = ['pk', 'content', 'status', ]
    list_filter = ['priority', 'status', 'tipologies']
    list_per_page = 25
    list_select_related = True
    radio_fields = {'priority': admin.HORIZONTAL}
    search_fields = ['content', 'user__username', 'user__first_name',
                     'user__last_name', 'requester__username',
                     'requester__first_name', 'requester__last_name']

    fieldsets = (
        (None, {
            "fields": ["tipologies", "priority", "content"],
        }),
        (_("Related tickets"), {
            "classes": ("collapse-closed",),
            "fields": ("related_tickets",)
        }),
    )

    def get_request_helpdeskuser(self, request):
        return HelpdeskUser.objects.get(pk=request.user.pk)

    def get_fieldsets(self, request, obj=None):
        user = self.get_request_helpdeskuser(request)
        fieldset = super(TicketAdmin, self).get_fieldsets(request, obj=obj)
        if user.is_superuser or user.is_operator() or user.is_admin():
            fieldset = deepcopy(fieldset)
            fieldset[0][1]['fields'].append('requester')
        return fieldset

    def get_list_filter(self, request):
        user = self.get_request_helpdeskuser(request)
        list_filter = super(TicketAdmin, self).get_list_filter(request)
        if user.is_superuser or user.is_operator() or user.is_admin():
            list_filter = list(list_filter) + ['requester', 'assignee']
        return list_filter

    # def get_queryset(self, request):
    #     user = self.get_request_helpdeskuser(request)
    #     qs = super(OwnableAdmin, self).queryset(request)
    #     if user.is_superuser or user.is_operator() or user.is_admin():
    #         return qs
    #     return qs.filter(user__id=request.user.id)

    def save_model(self, request, obj, form, change):
        if obj.requester_id is None:
            obj.requester = request.user
        return super(TicketAdmin, self).save_model(request, obj, form, change)


    # def add_view(self, request, form_url='', extra_context=None):
    #
    #     if request.method == 'POST':
    #         print(request.POST)
    #     return super(TicketAdmin, self).add_view(
    #         request, form_url=form_url, extra_context=extra_context)
    #
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     if request.method == 'POST':
    #         print(request.POST)
    #
    #     return super(TicketAdmin, self).change_view(
    #         request, object_id, form_url=form_url, extra_context=extra_context)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tipology, TipologyAdmin)
admin.site.register(Ticket, TicketAdmin)
