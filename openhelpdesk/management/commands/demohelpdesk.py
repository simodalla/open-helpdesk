# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection
from django.template import Template, Context
from mezzanine.utils.models import get_user_model
from mezzanine.utils.sites import current_site_id

from six.moves import cStringIO
from openhelpdesk.management.commands import inithelpdesk
from openhelpdesk.models import (HelpdeskUser, Category, Ticket, Message, Report,
                             PRIORITIES, Tipology, Source)
from openhelpdesk.defaults import (
    HELPDESK_REQUESTERS, HELPDESK_OPERATORS, HELPDESK_ADMINS)


User = get_user_model()


class Command(BaseCommand):
    """
    Execute init operation for openhelpdesk app. Create default group with relative
    permissions.
    """

    can_import_settings = True
    usage = lambda foo, bar: ("usage: %prog [appname1] [appname2] [options] "
                              "\n" + str(Command.__doc__.rstrip()))

    app_label = 'openhelpdesk'

    def handle(self, *apps, **options):
        requester = None
        from django.conf import settings
        settings.INSTALLED_APPS = (
            list(settings.INSTALLED_APPS) + ['django.contrib.webdesign'])

        inithelpdesk.Command().execute(stdout=cStringIO(), stderr=cStringIO())

        default_site = Site.objects.get(pk=current_site_id())

        [source.sites.add(default_site) for source in Source.objects.all()]

        for c in range(0, 5):
            category, c_created = Category.objects.get_or_create(
                title='category {}'.format(c))
            for i in range(0, 5):
                category.tipologies.get_or_create(
                    title='tipology {}'.format(i))
            [t.sites.add(default_site) for t in category.tipologies.all()]

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

            t = Template("{% load webdesign %} {% lorem 5 w random %}.")
            tipologies = Tipology.objects.all()
            cursor = connection.cursor()
            user = User.objects.get(pk=huser.pk)
            if group_name == HELPDESK_REQUESTERS[0]:
                requester = user
                Ticket.objects.all().delete()
                for table in ['ticket', 'message']:
                    cursor.execute("SELECT setval("
                                   "'public.openhelpdesk_{}_id_seq',"
                                   "  1, true);".format(table))

                for n, priority in enumerate(PRIORITIES):
                    ticket = Ticket()
                    ticket.priority = priority[0]
                    ticket.requester = user
                    ticket.content = t.render(Context({}))
                    ticket.site = default_site
                    ticket.source = Source.objects.get(
                        code='web_site' if n % 2 == 1 else 'email')
                    ticket.save()
                    ticket.tipologies.add(*tipologies[0:2])
                    ticket.initialize()

                    [ticket.messages.create(
                        content=Template("{% load webdesign %} {% lorem 5 w"
                                         " random %}.").render(Context({})),
                        sender=user) for ti in range(0, 3)]

                print("Tickets", Ticket.objects.all(), sep=": ")
                print("Messages", Message.objects.all(), sep=": ")
                print("Reports", Report.objects.all(), sep=": ")

            if group_name == HELPDESK_OPERATORS[0]:
                for n, ticket in enumerate(Ticket.objects.all()):
                    [Report.objects.create(
                        ticket=ticket, sender=user, recipient=requester,
                        content=Template("{% load webdesign %} {% lorem 5 w"
                                         " random %}.").render(Context({})))
                     for ri in range(0, 3)]
                    if n % 2 == 1:
                        ticket.opening(user)
