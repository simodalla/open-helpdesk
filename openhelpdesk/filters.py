from datetime import date

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import OrganizationSetting


class StatusListFilter(admin.ChoicesFieldListFilter):
    title = _('Status')

    def __init__(self, *args, **kwargs):
        super(StatusListFilter, self).__init__(*args, **kwargs)
        self.title = StatusListFilter.title


class EmailDomainFilter(admin.SimpleListFilter):
    title = _('Domain of email')

    parameter_name = 'domain'

    def lookups(self, request, model_admin):
        return tuple([(os.email_domain, os.filter_label or os.title)
                      for os in OrganizationSetting.objects.iterator()])

    def queryset(self, request, queryset):
        # print(self.value)

        if self.value():
            queryset = queryset.filter(
                requester__email__icontains=self.value())

        return queryset
