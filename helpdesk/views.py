# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView

from braces.views import GroupRequiredMixin

from mezzanine.conf import settings

from .models import Ticket, TICKET_STATUS_OPEN

settings.use_editable()


class OpenTicketView(GroupRequiredMixin, RedirectView):
    group_required = [settings.HELPDESK_OPERATORS,
                      settings.HELPDESK_ADMINS]
    permanent = False

    def get(self, request, *args, **kwargs):
        kwargs.update({'request_user': request.user})
        return super(OpenTicketView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        ticket_pk = kwargs.get('pk')
        try:
            ticket = Ticket.objects.get(pk=ticket_pk)
            ticket.assignee = kwargs.get('request_user')
            ticket.status = TICKET_STATUS_OPEN
            # ticket.save()
            # TODO: messaggio di successo
        except Ticket.DoesNotExist:
            # TODO: messaggio di error
            return reverse(admin_urlname(Ticket._meta, 'changelist'))
        return reverse(admin_urlname(Ticket._meta, 'change'),
                       args=(ticket_pk,))

