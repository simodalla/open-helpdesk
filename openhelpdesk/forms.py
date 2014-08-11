# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import forms
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import VERSION as DJANGO_VERSION
from mezzanine.conf import settings
from mezzanine.utils.sites import current_site_id
from autocomplete_light import ModelForm as AutocompleteModelForm

from .models import Ticket, Report, Source


class TicketAdminForm(forms.ModelForm):

    _ohp_only_operators_fields = ['requester', 'source']

    def __init__(self, *args, **kwargs):
        super(TicketAdminForm, self).__init__(*args, **kwargs)
        # tipologies is filtered by current site if 'tipologies' in
        # self.fields. If field is read_only isn't in self.fields
        # for field, related_name in ('t')
        if 'content' in self.fields:
            self.fields['content'].required = True
            self.fields['content'].widget.attrs['class'] = 'mceEditor'
        if 'source' in self.fields:
            self.fields['source'].required = True
            try:
                self.fields['source'].initial = Source.get_default_obj()
            except Source.DoesNotExist:
                pass
        if not self.instance.pk:
            site = Site.objects.get(pk=current_site_id())
            for field, related_name in [('tipologies', 'helpdesk_tipologies'),
                                        ('source', 'helpdesk_sources')]:
                if field in self.fields:
                    relate_manager = getattr(site, related_name, None)
                    if relate_manager:
                        self.fields[field].queryset = relate_manager.all()

        # The next code is tricky for ensure compatibility with django 1.5
        if DJANGO_VERSION[0] == 1 and DJANGO_VERSION[1] < 6:  # django 1.5
            if self.instance.pk:  # change form
                for field in ['tipologies', 'priority', 'content']:
                    del self.fields[field]
            if len(args) > 0:  # the form is bound
                form_data = args[0]
                for field in self._ohp_only_operators_fields:
                    # if current field is not in buond data whereas is in
                    # self.fields therefore user is an "requester". We then
                    # remove field from form fields (self.fields)
                    if field not in form_data and field in self.fields:
                        del self.fields[field]

    def clean_tipologies(self):
        """
        Additional validation for 'tipologies' field. If the number of
        tipologies selected is greater than
        'HELPDESK_MAX_TIPOLOGIES_FOR_TICKET' setting, raise an ValidationError
        """
        settings.use_editable()
        max_tipologies = settings.HELPDESK_MAX_TIPOLOGIES_FOR_TICKET
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
