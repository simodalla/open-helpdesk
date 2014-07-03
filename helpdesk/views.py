# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import json

from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView, View
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
        url_on_error = reverse(admin_urlname(Ticket._meta, 'changelist'))
        error_msg_prefix = _('An error occurs.')
        try:
            ticket = Ticket.objects.get(pk=ticket_pk)
            ticket.opening(self.request.user)
            msg = _('Ticket n.%(pk)s is opened and assigned.') % {
                'pk': ticket_pk}
        except Ticket.DoesNotExist:
            msg = _('Ticket n.%(pk)s does not exist.') % {'pk': ticket_pk}
            messages.error(self.request, '{} {}'.format(error_msg_prefix, msg))
            return url_on_error
        except ValueError as ve:  # Errors raised by ticket.open
            messages.error(self.request, '{} {}'.format(error_msg_prefix,
                                                        str(ve)))
            return url_on_error
        messages.success(self.request, msg)
        return reverse(admin_urlname(Ticket._meta, 'change'),
                       args=(ticket_pk,))


class ObjectToolsView(GroupRequiredMixin, View):
    group_required = [settings.HELPDESK_REQUESTERS,
                      settings.HELPDESK_OPERATORS,
                      settings.HELPDESK_ADMINS]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # import ipdb
        # ipdb.set_trace()
        print(request.GET)
        print(args)
        print(kwargs)

        return HttpResponse(json.dumps([{'url': '/admin/helpdesk/',
                                         'text': 'pippo'},
                                        {'url': '/admin/helpdesk/',
                                         'text': 'pluto'},]),
                            content_type='application/json')