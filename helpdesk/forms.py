# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import forms
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.utils.sites import current_site_id

from autocomplete_light import ModelForm as AutocompleteModelForm

from .models import Ticket, Report


class TicketAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TicketAdminForm, self).__init__(*args, **kwargs)
        # tipologies is filtered by current site if 'tipologies' in
        # self.fields. If field is read_only isn't in self.fields
        if 'tipologies' in self.fields:
            site = Site.objects.get(pk=current_site_id())
            self.fields['tipologies'].queryset = site.tipologies.all()

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


class ReportAdminAutocompleteForm(AutocompleteModelForm):
    class Meta:
        model = Report
        autocomplete_fields = ('ticket',)
