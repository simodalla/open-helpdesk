# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.test import TestCase

from ..models import Category, Tipology, Attachment


class IssueCategoryTest(TestCase):
    def test_str_method(self):
        category = Category(title="foo")
        self.assertEqual("{}".format(category), "foo")


class IssueTipologyTest(TestCase):
    def test_str_method(self):
        tipology = Tipology(title="foo")
        self.assertEqual("{}".format(tipology), "foo")


# class AttachmentTest(TestCase):
#     def test_f(self):
#         Attachment
