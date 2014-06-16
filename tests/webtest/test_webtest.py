# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals, absolute_import
#
# from django.contrib.admin.templatetags.admin_urls import admin_urlname
# from django.core.urlresolvers import reverse
# from django.contrib.sites.models import Site
# from django_webtest import WebTest
#
# from helpdesk.models import Ticket
# from helpdesk.defaults import HELPDESK_REQUESTERS
#
# from .factories import UserFactory, GroupFactory
#
#
# class MyTestCase(WebTest):
#     def test_admin(self):
#         print(Site.objects.all())
#         requester = UserFactory(
#             groups=[GroupFactory(name=HELPDESK_REQUESTERS[0],
#                                  permissions=list(HELPDESK_REQUESTERS[1]))])
#         print(admin_urlname(Ticket._meta, 'add'))
#         index = self.app.get(
#             reverse(admin_urlname(Ticket._meta, 'add')), user=requester)
#         print(index.form)
#         # import pytest
#         # pytest.set_trace()