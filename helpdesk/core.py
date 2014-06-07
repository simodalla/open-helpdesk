# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

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

MGS_TICKET_NOT_IN_STATUS = _('Ticket not in status "%(status)s"')


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
