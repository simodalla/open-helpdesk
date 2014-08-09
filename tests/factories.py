from __future__ import absolute_import

import factory
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from mezzanine.core.models import SitePermission

from openhelpdesk.core import get_perm
from openhelpdesk.models import (Category, Tipology, HelpdeskUser as User,
                                 Ticket)


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)

    name = factory.Sequence(lambda n: 'group{0}'.format(n))

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            # We have a saved object and a list of permission names
            self.permissions.add(*[get_perm(pn) for pn in extracted])


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    FACTORY_DJANGO_GET_OR_CREATE = ('username',)

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    first_name = factory.Sequence(lambda n: 'John {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Doe {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password',
                                                'default')
    is_staff = True
    is_active = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if create and extracted:
            self.groups.add(*[group for group in extracted])

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            # We have a saved object and a list of permission names
            self.user_permissions.add(*[get_perm(pn) for pn in extracted])


class SiteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Site

    domain = factory.Sequence(lambda n: 'example{0}.com'.format(n))
    name = factory.Sequence(lambda n: 'example{0}'.format(n))


class SitePermissionF(factory.DjangoModelFactory):
    FACTORY_FOR = SitePermission


class HelpdeskerF(UserFactory):
    site_permission = factory.RelatedFactory(SitePermissionF, 'user')


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    title = factory.Sequence(lambda n: 'category{0}'.format(n))

    @factory.post_generation
    def tipologies(self, create, extracted, **kwargs):
        if create and extracted:
            [self.tipologies.create(title=title) for title in extracted]


class TipologyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Tipology

    title = factory.Sequence(lambda n: 'tipology{0}'.format(n))

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        if create and extracted:
            [self.sites.add(site) for site in extracted]


class TicketFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Ticket

    content = factory.Sequence(lambda n: 'content of ticket {0}'.format(n))

    @factory.post_generation
    def tipologies(self, create, extracted, **kwargs):
        if create and extracted:
            [self.tipologies.add(tipology) for tipology in extracted]
