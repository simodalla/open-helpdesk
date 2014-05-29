# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from braces.views import GroupRequiredMixin

from mezzanine.conf import settings

from .models import Ticket

settings.use_editable()


class OpenTicketView(GroupRequiredMixin, RedirectView):
    group_required = [settings.HELPDESK_OPERATORS,
                      settings.HELPDESK_ADMINS]
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        ticket_pk = kwargs.get('pk')
        ticket_changelist_url = reverse(admin_urlname(Ticket._meta,
                                                      'changelist'))
        error_msg_prefix = _('An error occurs.')
        try:
            ticket = Ticket.objects.get(pk=ticket_pk)
            ticket.open(self.request.user)
            msg = _('Ticket n.%(pk)s is opened and assigned.') % {
                'pk': ticket_pk}
            messages.success(self.request, msg)
        except Ticket.DoesNotExist:
            msg = _('Ticket n.%(pk)s does not exist.') % {'pk': ticket_pk}
            messages.error(self.request, '{} {}'.format(error_msg_prefix, msg))
            return ticket_changelist_url
        except ValueError as ve:
            messages.error(self.request, '{} {}'.format(error_msg_prefix,
                                                        str(ve)))
            return ticket_changelist_url
        return reverse(admin_urlname(Ticket._meta, 'change'),
                       args=(ticket_pk,))

