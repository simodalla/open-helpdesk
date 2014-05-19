# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.admin import TabularDynamicInlineAdmin, OwnableAdmin

from .models import Category, Tipology, Attachment, Ticket


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


class TicketAdmin(OwnableAdmin):
    filter_horizontal = ("tipologies", "related_tickets")
    inlines = [AttachmentInline]
    radio_fields = {"priority": admin.HORIZONTAL}

    fieldsets = (
        (None, {
            "fields": ["tipologies", "priority", "content"],
        }),
        (_("Related tickets"), {
            "classes": ("collapse-closed",),
            "fields": ("related_tickets",)
        }),
    )

    def __init__(self, *args, **kwargs):
        super(TicketAdmin, self).__init__(*args, **kwargs)
        try:
            self.search_fields = (list(set(
                list(self.search_fields) +
                list(self.model.objects.get_search_fields().keys()))))
        except AttributeError:
            pass

    def get_fieldsets(self, request, obj=None):
        fieldset = super(TicketAdmin, self).get_fieldsets(request, obj=obj)
        if request.user.is_superuser:
            fieldset = deepcopy(fieldset)
            fieldset[0][1]['fields'].append('requester')
        print(fieldset)
        return fieldset

    def save_form(self, request, form, change):
        """
        Set the object's owner as the logged in user.
        """
        obj = form.save(commit=False)
        print("*******", obj.requester_id)
        if obj.requester_id is None:
            obj.requester = request.user
        return super(TicketAdmin, self).save_form(request, form, change)

    def add_view(self, request, form_url='', extra_context=None):

        if request.method == 'POST':
            print(request.POST)
        return super(TicketAdmin, self).add_view(
            request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'POST':
            print(request.POST)

        return super(TicketAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tipology, TipologyAdmin)
admin.site.register(Ticket, TicketAdmin)
