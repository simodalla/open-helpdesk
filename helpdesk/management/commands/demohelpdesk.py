# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from six.moves import cStringIO

from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from helpdesk.management.commands import inithelpdesk
from helpdesk.models import HelpdeskUser, Category, Tipology
from helpdesk.defaults import (
    HELPDESK_REQUESTERS, HELPDESK_OPERATORS, HELPDESK_ADMINS)


class Command(BaseCommand):
    """
    Execute init operation for helpdesk app. Create default group with relative
    permissions.
    """

    can_import_settings = True
    usage = lambda foo, bar: ("usage: %prog [appname1] [appname2] [options] "
                              "\n" + Command.__doc__.rstrip())

    app_label = 'helpdesk'

    def handle(self, *apps, **options):

        inithelpdesk.Command().execute(stdout=cStringIO(), stderr=cStringIO())

        for group_name, pc in [HELPDESK_REQUESTERS, HELPDESK_OPERATORS,
                               HELPDESK_ADMINS]:
            username = group_name.rstrip('s')

            try:
                huser = HelpdeskUser.objects.get(username=username)
                self.stdout.write('User "{}" is already exists'.format(
                    username))
            except HelpdeskUser.DoesNotExist:
                huser = HelpdeskUser.objects.create_user(
                    username, email='{}@example.com'.format(username),
                    password=username)
                self.stdout.write('User "{}" is created'.format(username))
            huser.is_staff = True
            huser.save()
            huser.groups.add(Group.objects.get(name=group_name))
            self.stdout.write('Group "{}" is added to "{}"'.format(group_name,
                                                                   username))

        default_site = Site.objects.get(pk=1)
        for c in range(0, 5):
            category, c_created = Category.objects.get_or_create(
                title='category {}'.format(c))
            for i in range(0, 5):
                category.tipologies.get_or_create(
                    title='tipology {}'.format(i))
            [t.sites.add(default_site) for t in category.tipologies.all()]



