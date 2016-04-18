# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


HELPDESK_REQUESTERS = ('helpdesk_requesters', [
    'openhelpdesk.add_ticket', 'openhelpdesk.change_ticket',
    'openhelpdesk.add_attachment', 'openhelpdesk.change_attachment',
    'openhelpdesk.add_message',
])
HELPDESK_OPERATORS = ('helpdesk_operators', [
    'openhelpdesk.add_ticket', 'openhelpdesk.change_ticket',
    'openhelpdesk.add_attachment', 'openhelpdesk.change_attachment',
    'openhelpdesk.delete_attachment',
    'openhelpdesk.add_report', 'openhelpdesk.change_report',
])
HELPDESK_ADMINS = ('helpdesk_admins', [
    'openhelpdesk.add_ticket', 'openhelpdesk.change_ticket',
    'openhelpdesk.add_attachment', 'openhelpdesk.change_attachment',
    'openhelpdesk.delete_attachment',
    'openhelpdesk.add_report', 'openhelpdesk.change_report',
    'openhelpdesk.add_category', 'openhelpdesk.change_category',
    'openhelpdesk.delete_category',
    'openhelpdesk.add_tipology', 'openhelpdesk.change_tipology',
    'openhelpdesk.delete_tipology',
    'auth.add_user', 'auth.change_user',
    'auth.add_group', 'auth.change_group',
])
OPENHELPDESK_MAX_TIPOLOGIES_FOR_TICKET = 3
OPENHELPDESK_LDAP_OPERATOR_GROUPS = 'Domain Admins'
OPENHELPDESK_LDAP_REQUESTER_GROUPS = ''

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

register_setting(
    name="OPENHELPDESK_MAX_TIPOLOGIES_FOR_TICKET",
    label=_("N. max of tipologies for ticket"),
    description=_("The max number of tipologies which can be related to a "
                  "single ticket"),
    editable=True,
    default=OPENHELPDESK_MAX_TIPOLOGIES_FOR_TICKET,
)

register_setting(
    name="OPENHELPDESK_EMAIL_FOOTER",
    label=_("Footer of email notifications"),
    description=_("The text of footer of all notification emails."),
    editable=True,
    default="Questa email è generata automaticamente, si prega di non"
            " rispondere. Per qualunque informazione contattare l'ufficio"
            " Servizi Informatici all'indirizzo"
            " ced@example.com",
)

register_setting(
    name="OPENHELPDESK_EMAIL_FOOTER",
    label=_("Footer of email notifications"),
    description=_("The text of footer of all notification emails."),
    editable=True,
    default="Questa email è generata automaticamente, si prega di non"
            " rispondere. Per qualunque informazione contattare l'ufficio"
            " Servizi Informatici all'indirizzo"
            " ced@example.com",
)

register_setting(
    name="OPENHELPDESK_LDAP_OPERATOR_GROUPS",
    label=_("Ldap group mapping for openhelpdek operators"),
    description=_("Ldap group mapping for openhelpdek operators."),
    editable=True,
    default=OPENHELPDESK_LDAP_OPERATOR_GROUPS,
)

register_setting(
    name="OPENHELPDESK_LDAP_REQUESTER_GROUPS",
    label=_("Ldap group mapping for openhelpdek requesters"),
    description=_("Gruppi ldap (separati da virgola!) i cui utenti"
                  " diventeranno requester per openhelpdesk"),
    editable=True,
    default=OPENHELPDESK_LDAP_REQUESTER_GROUPS,
)
