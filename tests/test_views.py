# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.test import TestCase

from helpdesk.views import OpenTicketView

from .factories import UserFactory
from .helpers import TestViewHelper


class OpenTicketViewTest(TestViewHelper, TestCase):

    view_class = OpenTicketView

    def test_for_debug(self):

        request = self.build_request(user=UserFactory())
        print(request.user)
        # import ipdb
        # ipdb.set_trace()
        view = self.build_view(request)
        print(view.get_redirect_url())
