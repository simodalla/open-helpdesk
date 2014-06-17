# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import


from django.test import TestCase

from django.contrib.auth.models import User

ARGS = ('admin', 'admin@example.com', 'admin',)

import pytest


# class FooTest(TestCase):

@pytest.mark.django_db
class TestFoo():

    def test_1(self):
        User.objects.create_superuser(*ARGS)

    def test_2(self):
        User.objects.create_superuser(*ARGS)
