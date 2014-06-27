# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django import template

from helpdesk.models import Report, Message

register = template.Library()


@register.inclusion_tag('admin/helpdesk/ticket/message.html')
def format_ticket_message(message, **kwargs):
    if not issubclass(message.__class__, Message):
        raise TypeError("{} isn't subclass object of".format(message, Message))
    context = {'css_style': None, 'message': message,
               'css_class': 'form-row',
               'model': getattr(message._meta, 'model_name',
                                message._meta.module_name)}
    if 'css_class' in kwargs:
        context.update({'css_class': kwargs['css_class']})
    if isinstance(message, Report):
        context['css_style'] = 'text-align: right;'
    return context
