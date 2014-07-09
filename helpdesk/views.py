# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from importlib import import_module

import json

from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse, resolve
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
        return '{}#tab_changestatuslog'.format(
            reverse(admin_urlname(Ticket._meta, 'change'), args=(ticket_pk,)))


class ObjectToolsView(GroupRequiredMixin, View):
    group_required = [settings.HELPDESK_REQUESTERS,
                      settings.HELPDESK_OPERATORS,
                      settings.HELPDESK_ADMINS]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        view = request.GET.get('view', None)
        object_tools = []
        if view:
            resolved_view = resolve(view)
            # example: helpdesk, ticket, change from url_name
            # 'helpdesk_ticket_change'
            app_label, model_name, view_name = (
                resolved_view.url_name.split('_'))
            object_id = resolved_view.args[0] if resolved_view.args else None
            obj = None
            try:
                # dynamic import of module 'helpdesk.admin'
                app_admin_module = import_module(
                    '{}.{}'.format(app_label, resolved_view.app_name))
                if object_id:
                    # # dynamic import of module 'helpdesk.models'
                    models_module = import_module(
                        '{}.models'.format(app_label))
                    # model is class of model, (eg: Ticket)
                    model = getattr(models_module, model_name.capitalize())
                    obj = model.objects.get(pk=object_id)
                # get class of model admin (eg: TicketAdmin)
                object_tools = getattr(
                    app_admin_module,
                    '{}Admin'.format(
                        model_name.capitalize())).get_object_tools(
                    request, view_name, obj=obj)
            except KeyError:
                pass
            except Exception as ex:
                object_tools.append({'error': str(ex)})

        return HttpResponse(json.dumps(object_tools),
                            content_type='application/json')
