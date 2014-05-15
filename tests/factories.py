from __future__ import absolute_import

import factory

from django.contrib.auth.models import Group, Permission, User
from helpdesk.models import Category, Tipology


HELPDESK_ISSUE_MAKERS = 'helpdesk_issue_makers'


def _get_perm(perm_name):
    """
    Returns permission instance with given name.

    Permission name is a string like 'auth.add_user'.
    """
    app_label, codename = perm_name.split('.')
    return Permission.objects.get(
        content_type__app_label=app_label, codename=codename)


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group

    name = factory.Sequence(lambda n: 'group{0}'.format(n))

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            # We have a saved object and a list of permission names
            self.permissions.add(*[_get_perm(pn) for pn in extracted])


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    first_name = factory.Sequence(lambda n: 'John {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Doe {0}'.format(n))
    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = 'default'
    is_staff = True
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if create and extracted:
            self.groups.add(*[group for group in extracted])

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if create and extracted:
            # We have a saved object and a list of permission names
            self.user_permissions.add(*[_get_perm(pn) for pn in extracted])


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
