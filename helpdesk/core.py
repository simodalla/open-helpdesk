# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _


TICKET_STATUS_NEW = 'new'
TICKET_STATUS_OPEN = 'open'
TICKET_STATUS_PENDING = 'pending'
TICKET_STATUS_SOLVED = 'closed'
TICKET_STATUSES = (
    (TICKET_STATUS_NEW, _('New')),
    (TICKET_STATUS_OPEN, _('Open')),
    (TICKET_STATUS_PENDING, _('Pending')),
    (TICKET_STATUS_SOLVED, _('Closed')),
)
TICKET_STATUES_AWESOME_ICONS = {
    TICKET_STATUS_NEW: 'spinner',
    TICKET_STATUS_OPEN: 'cog',
    TICKET_STATUS_PENDING: 'lock',
    TICKET_STATUS_SOLVED: 'check-square'
}
MGS_TICKET_NOT_IN_STATUS = _('Ticket not in status "%(status)s"')

DEFAULT_SOURCES = [
    ('portal', _('Portal')),
    ('email', _('Email')),
    ('phone', _('Phone')),
    ('chat', _('Chat'))
]


class TicketStatusError(Exception):
    default_message = _('Ticket Status Error')

    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            args = tuple([self.__class__.default_message])
        super(TicketStatusError, self).__init__(*args, **kwargs)


class TicketIsNotNewError(TicketStatusError):
    default_message = (
        MGS_TICKET_NOT_IN_STATUS % {'status': TICKET_STATUSES[0][1]})


class TicketIsNotOpenError(TicketStatusError):
    default_message = (
        MGS_TICKET_NOT_IN_STATUS % {'status': TICKET_STATUSES[1][1]})


class TicketIsNotPendingError(TicketStatusError):
    default_message = (
        MGS_TICKET_NOT_IN_STATUS % {'status': TICKET_STATUSES[2][1]})


class TicketIsClosedError(TicketStatusError):
    default_message = (_('Ticket is already in "%(status)s" status') %
                       {'status': TICKET_STATUSES[3][1]})


def get_perm(perm_name):
    """
    Returns permission instance with given name.

    Permission name is a string like 'auth.add_user'.
    """
    app_label, codename = perm_name.split('.')
    return Permission.objects.get(
        content_type__app_label=app_label, codename=codename)
