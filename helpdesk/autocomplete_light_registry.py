# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.utils.translation import ugettext_lazy as _
import autocomplete_light

from .models import Ticket, HelpdeskUser


class TicketAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['id', 'content']
    attrs = {
        'placeholder': _('Type number of content...'),
        'data-autocomplete-minimum-characters': 1,
    }

    def choices_for_request(self):
        user = HelpdeskUser.objects.get(pk=self.request.user.pk)
        if user.is_requester():
            self.choices = self.choices.filter(requester=user)
        return super(TicketAutocomplete, self).choices_for_request()

autocomplete_light.register(Ticket, TicketAutocomplete)
