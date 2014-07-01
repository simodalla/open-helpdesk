# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection
from django.template import Template, Context
from mezzanine.utils.models import get_user_model

from six.moves import cStringIO
from helpdesk.management.commands import inithelpdesk
from helpdesk.models import (HelpdeskUser, Category, Ticket, Message, Report,
                             PRIORITIES, Tipology)
from helpdesk.defaults import (
    HELPDESK_REQUESTERS, HELPDESK_OPERATORS, HELPDESK_ADMINS)

User = get_user_model()


class Command(BaseCommand):
    """
    Execute init operation for helpdesk app. Create default group with relative
    permissions.
    """

    can_import_settings = True
    usage = lambda foo, bar: ("usage: %prog [appname1] [appname2] [options] "
                              "\n" + str(Command.__doc__.rstrip()))

    app_label = 'helpdesk'

    def handle(self, *apps, **options):
        requester = None
        from django.conf import settings
        settings.INSTALLED_APPS = (
            list(settings.INSTALLED_APPS) + ['django.contrib.webdesign'])

        inithelpdesk.Command().execute(stdout=cStringIO(), stderr=cStringIO())

        default_site = Site.objects.get(pk=1)
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

                for n, p in enumerate(PRIORITIES):
                    ticket, c = Ticket.objects.get_or_create(
                        pk=n + 1,
                        defaults={'priority': p[0],
                                  'requester': user,
                                  'content': t.render(Context({})),
                                  'site': default_site})
                    ticket.tipologies.add(*tipologies[0:2])
                    cursor.execute("SELECT setval('public.helpdesk_ticket"
                                   "_id_seq',  %s, true);", [n + 1])

                    [ticket.messages.create(
                        content=Template("{% load webdesign %} {% lorem 5 w"
                                         " random %}.").render(Context({})),
                        sender=user) for ti in range(0, 3)]

                print("Tickets", Ticket.objects.all(), sep=": ")
                print("Messages", Message.objects.all(), sep=": ")
                print("Reports", Report.objects.all(), sep=": ")

            if group_name == HELPDESK_OPERATORS[0]:
                for t in Ticket.objects.filter(
                        pk__in=list(range(1, len(PRIORITIES) + 1))):
                    [Report.objects.create(
                        ticket=t, sender=user, recipient=requester,
                        content=Template("{% load webdesign %} {% lorem 5 w"
                                         " random %}.").render(Context({})))
                     for ri in range(0, 3)]
