# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from mezzanine.conf import register_setting

HELPDESK_REQUESTERS = ('helpdesk_requesters', ['helpdesk.add_ticket',
                                               'helpdesk.change_ticket'])
HELPDESK_OPERATORS = ('helpdesk_operators', ['helpdesk.add_ticket',
                                             'helpdesk.change_ticket'])
HELPDESK_ADMINS = ('helpdesk_admins', ['helpdesk.add_ticket',
                                       'helpdesk.change_ticket',
                                       'helpdesk.add_category',
                                       'helpdesk.change_category',
                                       'helpdesk.delete_category',
                                       'helpdesk.add_tipology',
                                       'helpdesk.change_tipology',
                                       'helpdesk.delete_tipology'])

register_setting(
    name="HELPDESK_REQUESTERS",
    description="The group name of requesters.",
    editable=False,
    default=HELPDESK_REQUESTERS[0],
)

register_setting(
    name="HELPDESK_OPERATORS",
    description="The group name of helpdesk operator.",
    editable=False,
    default=HELPDESK_OPERATORS[0],
)

register_setting(
    name="HELPDESK_ADMINS",
    description="The group name of helpdesk admins.",
    editable=False,
    default=HELPDESK_ADMINS[0],
)
