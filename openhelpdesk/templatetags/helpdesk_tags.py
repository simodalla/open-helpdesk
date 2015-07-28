# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import Template, Context

from openhelpdesk.models import Message
from openhelpdesk.core import TICKET_STATUES_AWESOME_ICONS, HelpdeskUser


register = template.Library()


@register.inclusion_tag('admin/openhelpdesk/ticket/message.html',
                        takes_context=True)
def format_ticket_message(context, message, **kwargs):
    if not issubclass(message.__class__, Message):
        raise TypeError("{} isn't subclass object of".format(message, Message))
    tag_context = {'css_style': '', 'message': message,
                   'css_class': 'form-row',
                   'model': message._meta.model_name,
                   'can_view_report': False}
    if 'helpdesk_user' in context:
        hu = HelpdeskUser(context['helpdesk_user'])
        if hu.is_operator() or hu.is_admin():
            tag_context['can_view_report'] = True

    if 'css_class' in kwargs:
        tag_context.update({'css_class': kwargs['css_class']})
    try:
        if message.report:
            opts = message.report._meta
            tag_context.update({'model': opts.model_name,
                'css_style': 'text-align: right;',
                'view_url': '{}?id={}'.format(
                    reverse(admin_urlname(opts, 'changelist')),
                    message.report.pk)})
    except ObjectDoesNotExist:
        pass
    return tag_context


def _context_awesome_icon(name, list_icon=False, spin=False,
                          larger=None):
    return {'name': name, 'list': list_icon, 'spin': spin, 'larger': larger}


@register.inclusion_tag('openhelpdesk/awesome_icon.html')
def awesome_status_icon(status):
    name, spin = TICKET_STATUES_AWESOME_ICONS.get(status,
                                                  ('circle-o-notch', True))
    return _context_awesome_icon(name, spin=spin)


@register.inclusion_tag('openhelpdesk/awesome_icon.html')
def awesome_icon(name, spin=False, larger=None):
    return _context_awesome_icon(name, spin=spin, larger=larger)


@register.filter(is_safe=True)
def helpdesk_status(status, surround=None):
    from openhelpdesk.core import TICKET_STATUSES
    surround = surround if surround in ['b', 'i', 'em', 'strong'] else None
    result = ("{% load i18n helpdesk_tags %}"
              "{% awesome_status_icon status %}&nbsp;&nbsp;"
              "{% if surround %}<{{ surround }}>{% endif %}"
              "{{ title }}"
              "{% if surround %}</{{ surround }}>{% endif %}")
    t = Template(result)
    title = next((title for code, title in TICKET_STATUSES if code == status),
                 None)
    return t.render(Context({'status': status, 'surround': surround,
                             'title': title}))


@register.inclusion_tag('openhelpdesk/search_fields_info.html',
                        takes_context=True)
def search_fields_info(context, cl):
    get_info = getattr(cl.model_admin,
                       'get_search_fields_info',
                       lambda request: None)
    return {'search_fields_info': get_info(context['request'])}