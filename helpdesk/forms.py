# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import forms
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from mezzanine.conf import settings
from mezzanine.utils.sites import current_site_id
from autocomplete_light import ModelForm as AutocompleteModelForm

from .models import Ticket, Report, Source


class TicketAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TicketAdminForm, self).__init__(*args, **kwargs)
        # tipologies is filtered by current site if 'tipologies' in
        # self.fields. If field is read_only isn't in self.fields
        # for field, related_name in ('t')
        site = Site.objects.get(pk=current_site_id())
        for field, related_name in [('tipologies', 'helpdesk_tipologies'),
                                    ('source', 'helpdesk_sources')]:
            if field in self.fields:
                relate_manager = getattr(site, related_name, None)
                print(relate_manager)
                if relate_manager:
                    self.fields[field].queryset = relate_manager.all()
        if 'source' in self.fields:
            try:
                self.fields['source'].initial = Source.get_default_obj()
            except Source.DoesNotExist:
                pass

    def clean_tipologies(self):
        """
        Additional validation for 'tipologies' field. If the number of
        tipologies selected is greater than 'HELPDESK_TICKET_MAX_TIPOLOGIES'
        setting, raise an ValidationError
        """
        settings.use_editable()
        max_tipologies = settings.HELPDESK_TICKET_MAX_TIPOLOGIES
        tipologies = self.cleaned_data['tipologies']
        if len(tipologies) > max_tipologies:
            msg = _('Too many tipologies selected. You can select a maximum'
                    ' of %(max)s.') % {'max': max_tipologies}
            raise ValidationError(msg, code='too_many_tipologies')
        return self.cleaned_data['tipologies']


class TicketAdminAutocompleteForm(AutocompleteModelForm, TicketAdminForm):
    class Meta:
        model = Ticket
        autocomplete_fields = ('related_tickets', 'requester',)


# class ReportAdminForm(forms.ModelForm):
#
#     def __init__(self, *args, **kwargs):
#         super(ReportAdminForm, self).__init__(*args, **kwargs)
#         if 'action_on_ticket' in self.fields:
#             print(self.fields['action_on_ticket'].choices)


class ReportAdminAutocompleteForm(AutocompleteModelForm):
    class Meta:
        model = Report
        autocomplete_fields = ('ticket',)
