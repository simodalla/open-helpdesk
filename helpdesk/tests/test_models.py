# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from mock import Mock

from .factories import (UserFactory, GroupFactory, CategoryFactory,
                        TipologyFactory)
from ..models import Category, Tipology, Attachment, Issue


HELPDESK_ISSUE_MAKERS = 'helpdesk_issue_makers'


class CategoryTest(TestCase):
    def test_str_method(self):
        category = Category(title="foo")
        self.assertEqual("{}".format(category), "foo")

    def test_admin_tipologies(self):
        category = CategoryFactory()
        tipologies = [TipologyFactory(category=category) for i in range(0, 3)]
        print(tipologies)
        print(category.tipologies.all())
        admin_tipologies_result = '<br>'.join(
            ['<a href="{}?id={}">{}</a>'.format(
                reverse('admin:helpdesk_tipology_changelist'), t.pk, t.title)
             for t in category.tipologies.all()])
        print(admin_tipologies_result)


class TipologyTest(TestCase):
    def test_str_method(self):
        tipology = Tipology(title="foo", category=Category(title="bar"))
        self.assertEqual("{}".format(tipology), "[bar] foo")


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

    def test_set_user_on_save(self):

        issue = Issue(user=self.issue_maker)
        issue.save()
        print("***************")
        print(issue.title)
        print("----", issue)
        print("----", issue.site)
        print("----", issue.slug)


