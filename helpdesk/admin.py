# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.admin import TabularDynamicInlineAdmin, OwnableAdmin

from .models import Category, Tipology, Attachment, Ticket


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'admin_tipologies']
    search_fields = ['title']


class TipologyAdmin(admin.ModelAdmin):
    list_display = ['title', 'admin_category', 'admin_sites']
    list_filter = ['category']
    search_fields = ['title', 'category__title']


class AttachmentInline(TabularDynamicInlineAdmin):
    extra = 1
    model = Attachment


class TicketAdmin(OwnableAdmin):
    filter_horizontal = ("tipologies", "related_tickets")
    inlines = [AttachmentInline]

    fieldsets = (
        (None, {
            "fields": ["tipologies", "content", ],
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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tipology, TipologyAdmin)
admin.site.register(Ticket, TicketAdmin)
