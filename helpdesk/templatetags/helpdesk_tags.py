# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Template, Context

from helpdesk.models import Message
from helpdesk.core import TICKET_STATUES_AWESOME_ICONS


register = template.Library()


@register.inclusion_tag('admin/helpdesk/ticket/message.html')
def format_ticket_message(message, **kwargs):
    if not issubclass(message.__class__, Message):
        raise TypeError("{} isn't subclass object of".format(message, Message))
    context = {'css_style': '', 'message': message,
               'css_class': 'form-row',
               'model': getattr(message._meta, 'model_name',
                                message._meta.module_name)}
    if 'css_class' in kwargs:
        context.update({'css_class': kwargs['css_class']})
    try:
        if message.report:
            context.update({'model': getattr(
                message.report._meta, 'model_name',
                message.report._meta.module_name),
                'css_style': 'text-align: right;'})
    except ObjectDoesNotExist:
        pass
    return context


def _context_awesome_icon(name, list_icon=False, spin=False,
                          larger=None):
    return {'name': name, 'list': list_icon, 'spin': spin, 'larger': larger}


@register.inclusion_tag('helpdesk/awesome_icon.html')
def awesome_status_icon(status):
    name, spin = TICKET_STATUES_AWESOME_ICONS.get(status,
                                                  ('circle-o-notch', True))
    return _context_awesome_icon(name, spin=spin)


@register.inclusion_tag('helpdesk/awesome_icon.html')
def awesome_icon(name, spin=False, larger=None):
    return _context_awesome_icon(name, spin=spin, larger=larger)


@register.filter(is_safe=True)
def helpdesk_status(status, surround=None):
    surround = surround if surround in ['b', 'i', 'em', 'strong'] else None
    result = ("{% load helpdesk_tags %}"
              "{% awesome_status_icon status %}&nbsp;&nbsp;"
              "{% if surround %}<{{ surround }}>{% endif %}"
              "{{ status|capfirst }}"
              "{% if surround %}</{{ surround }}>{% endif %}")
    t = Template(result)
    return t.render(Context({'status': status, 'surround': surround}))

