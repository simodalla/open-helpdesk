from datetime import date
import functools
import operator

from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings

from .core import HelpdeskUser
from .models import OrganizationSetting, Subteam


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
        if self.value():
            queryset = queryset.filter(
                requester__email__icontains=self.value())
        return queryset


class SubteamFilter(admin.SimpleListFilter):
    title = _('Subteam')

    parameter_name = 'subteam'

    def lookups(self, request, model_admin):
        return tuple([(os.title, os.title.capitalize())
                      for os in Subteam.objects.iterator()])

    def queryset(self, request, queryset):
        q_title = self.value()
        if q_title:
            subteam = Subteam.objects.get(title=q_title)
            organizations_managed = subteam.organizations_managed.all()
            if organizations_managed.count():
                ors = [Q(requester__email__icontains=o.email_domain)
                       for o in subteam.organizations_managed.all()]
                queryset = queryset.filter(functools.reduce(operator.or_, ors))
        return queryset


class AssegneeFilter(admin.SimpleListFilter):
    title = _('Assignee')

    parameter_name = 'assignee'

    def lookups(self, request, model_admin):

        operators = HelpdeskUser.get_user_model().objects.filter(groups__name__in=[
            settings.HELPDESK_OPERATORS,
            settings.HELPDESK_ADMINS],
            is_active=True).order_by('first_name', 'last_name').distinct(
            'first_name', 'last_name').iterator()
        # return super(AssegneeFilter, self).lookups(request, model_admin)
        return tuple([(assignee.id, '{} {}'.format(assignee.first_name.capitalize(),
                                                   assignee.last_name.capitalize()))
                      for assignee in operators])

    def queryset(self, request, queryset):
        q_id = self.value()
        if q_id:
            return queryset.filter(assignee__id=q_id)
        return queryset