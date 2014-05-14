# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin

from mezzanine.core.admin import TabularDynamicInlineAdmin

from .models import Category, Tipology, Attachment, Issue


class CategoryAdmin(admin.ModelAdmin):
    pass


class TipologyAdmin(admin.ModelAdmin):
    pass


class AttachmentInline(TabularDynamicInlineAdmin):
    extra = 1
    model = Attachment


class IssueAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tipology, TipologyAdmin)
admin.site.register(Issue, IssueAdmin)
