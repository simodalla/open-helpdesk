# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

import autocomplete_light

from mezzanine.conf import settings
from mezzanine.utils.sites import current_site_id

from .models import Ticket
from .core import HelpdeskUser

User = get_user_model()


class TicketAutocomplete(autocomplete_light.AutocompleteModelBase):
    attrs = {
        'placeholder': _('Type id or content for search Ticket...'),
        'data-autocomplete-minimum-characters': 1,
    }
    search_fields = ['id', 'content']

    def choices_for_request(self):
        # user = HelpdeskUser(.objects.get(pk=self.request.user.pk)
        hu = HelpdeskUser(self.request)
        if hu.is_requester():
            self.choices = self.choices.filter(requester=hu.user)
        if hu.is_operator():
            self.choices = self.choices.filter(site__id=current_site_id())
        return super(TicketAutocomplete, self).choices_for_request()

    def choice_label(self, choice):
        return "n.{} [{}]".format(choice.id, choice.get_clean_content(10))


class RequesterAutocomplete(autocomplete_light.AutocompleteModelBase):
    attrs = {
        'placeholder': _('Type text for search Requester...'),
        'data-autocomplete-minimum-characters': 2,
    }
    choices = User.objects.filter(groups__name=settings.HELPDESK_REQUESTERS)
    search_fields = ['username', 'last_name', 'first_name', 'email']


autocomplete_light.register(Ticket, TicketAutocomplete)
autocomplete_light.register(User, RequesterAutocomplete)
