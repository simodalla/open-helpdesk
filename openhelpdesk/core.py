# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import collections

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
    TICKET_STATUS_NEW: ('spinner', True,),
    TICKET_STATUS_OPEN: ('cog', True,),
    TICKET_STATUS_PENDING: ('lock', False,),
    TICKET_STATUS_SOLVED: ('check-square', False,)
}

DEFAULT_SOURCES = [
    ('web_site', _('Web Site'), 'desktop'),
    ('email', _('Email'), 'envelope'),
    ('phone', _('Phone'), 'phone'),
    ('chat', _('Chat'), 'wechat')
]

ACTIONS_ON_TICKET = collections.OrderedDict()
ACTIONS_ON_TICKET['no_action'] = _('No action (maintain the current status)')
ACTIONS_ON_TICKET['put_on_pending'] = _('Put on pending')
ACTIONS_ON_TICKET['remove_from_pending'] = _('Remove from pending')
ACTIONS_ON_TICKET['close'] = _('Close')
DEFAULT_ACTIONS = ['no_action']


MGS_TICKET_NOT_IN_STATUS = _('Ticket not in status "%(status)s"')
MGS_TICKET_ALREADY_IN_STATUS = _('Ticket is already in "%(status)s" status')


class TicketStatusError(Exception):
    default_message = _('Ticket Status Error')

    def __init__(self, status=None, *args, **kwargs):
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
    default_message = (MGS_TICKET_ALREADY_IN_STATUS %
                       {'status': TICKET_STATUSES[3][1]})


class TicketIsOpenError(TicketStatusError):
    default_message = (MGS_TICKET_ALREADY_IN_STATUS %
                       {'status': TICKET_STATUSES[1][1]})


class TicketIsNewError(TicketStatusError):
    default_message = (_('The ticket is still in "%(status)s" status') %
                       {'status': TICKET_STATUSES[0][1]})


def get_perm(perm_name):
    """
    Returns permission instance with given name.

    Permission name is a string like 'auth.add_user'.
    """
    app_label, codename = perm_name.split('.')
    return Permission.objects.get(
        content_type__app_label=app_label, codename=codename)
