import logging

from django.contrib.auth.models import Group
from django.core.mail import mail_managers
from django.template import loader, Context

from mezzanine.conf import settings
from mezzanine.utils.email import subject_template

from waffle import switch_is_active

from pautils.ldap_backends import MezzanineLDAPBackend

logger = logging.getLogger(__name__)


class OpenHelpdeskLDAPBackend(MezzanineLDAPBackend):
    @property
    def ldap_requester_groups(self):
        return settings.OPENHELPDESK_LDAP_REQUESTER_GROUPS.split(',')

    @property
    def ldap_operator_groups(self):
        return settings.OPENHELPDESK_LDAP_OPERATOR_GROUPS.split(',')

    def _check_validity_group(self, ldap_groups, ldap_user):
        s_groups_to_check = set(map(lambda x: x.strip().lower(), ldap_groups))
        s_container = set(
            map(lambda x: x.strip().lower(), ldap_user.group_names))
        return bool(s_groups_to_check.intersection(s_container))

    def check_validity_requester(self, ldap_user):
        return self._check_validity_group(self.ldap_requester_groups, ldap_user)

    def check_validity_operator(self, ldap_user):
        return self._check_validity_group(self.ldap_operator_groups, ldap_user)

    @staticmethod
    def send_email_report(user, ldap_user):
        template = "openhelpdesk/email/report/ldap_backend/on_creation"
        context = {'user': user}
        subject = subject_template("{}_subject.txt".format(template), context)
        context.update(
            {'ldap_user': ldap_user,
             'groups': user.groups.order_by('name').values_list(
                 'name', flat=True),
             'domains': user.sitepermissions.sites.order_by('pk').values_list(
                 'domain', flat=True),
             'user_opts': user._meta},)
        message = loader.get_template("{}.txt".format(template)).render(
            Context(context))
        mail_managers(subject, message, True)
        return True

    def get_or_create_user(self, username, ldap_user):
        user, create = super(OpenHelpdeskLDAPBackend, self).get_or_create_user(
            username, ldap_user)
        try:
            if create and self.check_validity_operator(ldap_user):
                user.groups.add(
                    Group.objects.get(name=settings.HELPDESK_OPERATORS))
            elif create and self.check_validity_requester(ldap_user):
                user.groups.add(
                    Group.objects.get(name=settings.HELPDESK_REQUESTERS))
        except Group.DoesNotExist as dne:
            logger.exception("Openhelpdeks groups error into "
                             "{}".format(self.__class__.__name__))
        except:
            logger.exception("Generic error into {}".format(
                self.__class__.__name__), exc_info=True)
        if create and switch_is_active(
                'openhelpdesk_ldapbackend_send_email_report'):
            self.send_email_report(user, ldap_user)
        return user, create
