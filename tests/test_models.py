# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.test import TestCase

from .factories import (CategoryFactory, UserFactory,
                        SiteFactory, TipologyFactory)
from django.contrib.auth.models import User
from helpdesk.models import Category, Tipology


class CategoryTest(TestCase):
    def test_str_method(self):
        category = Category(title="foo")
        self.assertEqual("{}".format(category), "foo")

    def test_admin_tipologies(self):
        category = CategoryFactory()
        admin_tipologies_result = '<br>'.join(
            ['<a href="{}?id={}" class="view_tipology">{}</a>'.format(
                reverse('admin:helpdesk_tipology_changelist'), t.pk, t.title)
             for t in category.tipologies.all()])
        self.assertEqual(category.admin_tipologies(), admin_tipologies_result)


class TipologyTest(TestCase):

    def test_str_method(self):
        tipology = Tipology(title="foo", category=Category(title="bar"))
        self.assertEqual("{}".format(tipology), "[bar] foo")

    def test_admin_sites(self):
        tipology = TipologyFactory(category=CategoryFactory(),
                                   sites=[SiteFactory() for i in range(0, 2)])
        admin_sites_result = '<br>'.join(
            ['<a href="{url}?id={site.id}" class="view_site">{site.domain}'
             '</a>'.format(url=reverse('admin:sites_site_changelist'), site=s)
             for s in tipology.sites.all()])
        self.assertEqual(tipology.admin_sites(), admin_sites_result)

    def test_admin_category(self):
        tipology = TipologyFactory(category=CategoryFactory(),
                                   sites=[SiteFactory() for i in range(0, 2)])
        admin_category_result = (
            '<a href="{url}?id={category.pk}" class="view_category">'
            '{category.title}</a>'.format(
                url=reverse('admin:helpdesk_category_changelist'),
                category=tipology.category))
        self.assertEqual(tipology.admin_category(), admin_category_result)


class HelpdeskUserTest(TestCase):
    def test_is_requester(self):

        user = UserFactory()
        print(type(user))
        auth_user = User.objects.get(pk=user.pk)
        print(type(auth_user))
        # helpdesk_user = HelpdeskUser.objects.get(pk=user.pk)
        # print(type(helpdesk_user))
        # import ipdb
        # ipdb.set_trace()
