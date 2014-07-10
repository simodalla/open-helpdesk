# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.utils.translation import ugettext_lazy as _

import autocomplete_light

from mezzanine.conf import settings
from mezzanine.utils.models import get_user_model
from mezzanine.utils.sites import current_site_id

from .models import Ticket, HelpdeskUser

User = get_user_model()


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
        if user.is_operator():
            self.choices = self.choices.filter(site__id=current_site_id())
        return super(TicketAutocomplete, self).choices_for_request()

    def choice_label(self, choice):
        return "n.{} [{}]".format(choice.id, choice.get_clean_content(10))


class RequesterAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['username', 'last_name', 'first_name', 'email']
    choices = User.objects.filter(groups__name=settings.HELPDESK_REQUESTERS)


autocomplete_light.register(Ticket, TicketAutocomplete)
autocomplete_light.register(User, RequesterAutocomplete)
