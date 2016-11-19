# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection

from mezzanine.core.management.commands import createdb
from mezzanine.utils.sites import current_site_id

from openhelpdesk.core import DEFAULT_SOURCES
from openhelpdesk.defaults import (
    HELPDESK_REQUESTERS, HELPDESK_OPERATORS, HELPDESK_ADMINS)
from openhelpdesk.models import Source


class Command(BaseCommand):
    """
    Execute init operation for openhelpdesk app. Create default group with
    relative permissions.
    """

    can_import_settings = True

    app_label = 'openhelpdesk'

    def handle(self, *args, **options):

        if "conf_setting" not in connection.introspection.table_names():
            createdb.Command.execute(**{'no_data': True})

        for group_name, permission_codenames in [HELPDESK_REQUESTERS,
                                                 HELPDESK_OPERATORS,
                                                 HELPDESK_ADMINS]:
            group, created = Group.objects.get_or_create(name=group_name)
            self.stdout.write('Group {} {}.\n'.format(
                group.name, 'created' if created else 'already exist'))

            for permission in permission_codenames:
                group.permissions.add(Permission.objects.get(
                    content_type__app_label=permission.split('.')[0],
                    codename=permission.split('.')[1]))
            self.stdout.write('Add permissions to {}: {}.\n\n'.format(
                group.name, permission_codenames))

        site = Site.objects.get(pk=current_site_id())
        for code, title, icon in DEFAULT_SOURCES:
            source, created = Source.objects.get_or_create(
                code=code, defaults={'title': title, 'icon': icon})
            if created:
                source.sites.add(site)
