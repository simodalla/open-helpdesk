# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from mock import Mock

from .factories import (UserFactory, GroupFactory, CategoryFactory,
                        SiteFactory,
                        TipologyFactory, HELPDESK_ISSUE_MAKERS)
from helpdesk.models import Category, Tipology, Issue


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


@override_settings(HELPDESK_ISSUE_MAKERS=HELPDESK_ISSUE_MAKERS)
class IssueTest(TestCase):
    def setUp(self):
        self.issue_maker = UserFactory(groups=(
            GroupFactory(name=HELPDESK_ISSUE_MAKERS,
                         permissions=('helpdesk.add_issue',)),))

    def test_set_data_from_request(self):
        mock_request = Mock(user=self.issue_maker)
        issue = Issue()
        issue.set_data_from_request(mock_request)
        self.assertEqual(issue.user, self.issue_maker)

    # def test_set_user_on_save(self):
    #     issue = Issue(user=self.issue_maker)
    #     issue.save()
    #     print("***************")
    #     print(issue.title)
    #     print("----", issue)
    #     print("----", issue.site)
    #     print("----", issue.slug)


