from __future__ import absolute_import

import factory
from openhelpdesk.core import get_perm


class GroupFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'auth.Group'
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'group{0}'.format(n))

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            # We have a saved object and a list of permission names
            self.permissions.add(*[get_perm(pn) for pn in extracted])


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)

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

    @factory.post_generation
    def sitepermissions(self, create, extracted, **kwargs):
        if create and extracted:
            # We have a saved object and a list of permission names
            self.sitepermissions.add(*[get_perm(pn) for pn in extracted])


class SiteFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'sites.Site'

    domain = factory.Sequence(lambda n: 'example{0}.com'.format(n))
    name = factory.Sequence(lambda n: 'example{0}'.format(n))


class SitePermissionF(factory.DjangoModelFactory):

    class Meta:
        model = 'core.SitePermission'


class HelpdeskerF(UserFactory):
    site_permission = factory.RelatedFactory(SitePermissionF, 'user')


class CategoryFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'openhelpdesk.Category'
        django_get_or_create = ('title',)

    title = factory.Sequence(lambda n: 'category{0}'.format(n))

    @factory.post_generation
    def tipologies(self, create, extracted, **kwargs):
        if create and extracted:
            [self.tipologies.create(title=title) for title in extracted]


class TipologyFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'openhelpdesk.Tipology'
        django_get_or_create = ('title',)

    title = factory.Sequence(lambda n: 'tipology{0}'.format(n))

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        if create and extracted:
            [self.sites.add(site) for site in extracted]


class TicketFactory(factory.DjangoModelFactory):

    class Meta:
        model = 'openhelpdesk.Ticket'

    content = factory.Sequence(lambda n: 'content of ticket {0}'.format(n))

    @factory.post_generation
    def tipologies(self, create, extracted, **kwargs):
        if create and extracted:
            [self.tipologies.add(tipology) for tipology in extracted]


class SubteamF(factory.DjangoModelFactory):

    class Meta:
        model = 'openhelpdesk.Subteam'

    title = factory.Sequence(lambda n: 'subteam{0}'.format(n))


class TeammateSettingF(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'openhelpdesk.TeammateSetting'

