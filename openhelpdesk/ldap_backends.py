from django.contrib.auth.models import Group

from mezzanine.conf import settings

from pautils.ldap_backends import MezzanineLDAPBackend


class OpenHelpdeskLDAPBackend(MezzanineLDAPBackend):
    @property
    def ldap_requester_groups(self):
        return settings.OPENHELPDESK_LDAP_REQUESTER_GROUPS.split(',')

    @property
    def ldap_operator_groups(self):
        return settings.OPENHELPDESK_LDAP_OPERATOR_GROUPS.split(',')

    def _check_validity_group(self, ldap_groups, ldap_user):
        s_groups_to_check = set(map(lambda x: x.strip().lower(), ldap_groups))
        s_container = set(map(lambda x: x.strip().lower(), ldap_user.group_names))
        return bool(s_groups_to_check.intersection(s_container))

    def check_validity_requester(self, ldap_user):
        return self._check_validity_group(self.ldap_requester_groups, ldap_user)

    def check_validity_operator(self, ldap_user):
        return self._check_validity_group(self.ldap_requester_groups, ldap_user)

    def get_or_create_user(self, username, ldap_user):
        user, create = super(OpenHelpdeskLDAPBackend, self).get_or_create_user(
            username, ldap_user)
        # print("*** ", user, create)
        if create and self.check_validity_operator(ldap_user):
            print("==>", settings.HELPDESK_OPERATORS)
            try:
                user.groups.add(
                    Group.objects.get(name=settings.HELPDESK_OPERATORS))
            except Group.DoesNotExist:
                # TODO far e il logging
                pass

        return user, create
