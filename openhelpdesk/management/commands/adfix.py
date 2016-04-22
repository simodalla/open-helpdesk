# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings

import ldap
from pprint import pprint

DATA_ENTI = [
    ('ASC', 'ascinsieme.it'),
    ('Casalecchio', 'comune.casalecchio.bo.it'),
    ('Adopera,OU=Casalecchio', 'adoperasrl.it'),
    ('Monte San Pietro', 'comune.montesanpietro.bo.it'),
    ('Sasso', 'comune.sassomarconi.bo.it'),
    ('Valsamoggia', 'comune.valsamoggia.bo.it'),
    ('Zola', 'comune.zolapredosa.bo.it')
]


class Command(NoArgsCommand):
    can_import_settings = True
    app_label = 'openhelpdesk'

    def get_email(self, username, domain):
        # print(type(username))
        result = '{}@{}'.format(username.decode("utf-8").lower(), domain)
        return result.encode("utf-8")

    def handle_noargs(self, **options):

        con = ldap.initialize('ldap://10.180.0.2')
        try:
            con.protocol_version = ldap.VERSION3
            con.set_option(ldap.OPT_REFERRALS, 0)
            attributes = ['displayName', 'company', 'mail',
                          'sn', 'givenName', 'memberOf', 'sAMAccountName']
            bind = con.simple_bind_s(settings.AUTH_LDAP_BIND_DN,
                                     settings.AUTH_LDAP_BIND_PASSWORD)
            criteria = "(&(objectClass=user))"
            base = "OU=Utenti,OU={}," + settings.AUTH_LDAP_BASE_UCRLS
            for ente, domain in DATA_ENTI:
                dn_ente = base.format(ente)
                result = con.search_s(dn_ente, ldap.SCOPE_SUBTREE,
                                      # criteria)
                                      criteria, attributes)
                for ldap_user in result:
                    # mod_attrs = [[ldap.MOD_ADD, 'email']]
                    if 'mail' not in ldap_user[1]:
                        mod_attrs = [
                            (ldap.MOD_ADD, 'mail', self.get_email(
                                ldap_user[1]['sAMAccountName'][0], domain))]
                        result = con.modify_s(str(ldap_user[0]), mod_attrs)
                        print(ldap_user[0], result)
        except Exception as e:
            raise e
        finally:
            con.unbind()
