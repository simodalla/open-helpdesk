# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals, absolute_import
#
# import pytest
#
# from django.contrib.admin.templatetags.admin_urls import admin_urlname
# from django.test import LiveServerTestCase
#
# from selenium.webdriver.firefox.webdriver import WebDriver
#
# from openhelpdesk.models import Ticket, PRIORITY_NORMAL
# from ..conftest import requester
#
#
# @pytest.mark.livetest
# class MySeleniumTests(LiveServerTestCase):
#
#     def get(self, url, *args, **kwargs):
#         from django.core.urlresolvers import reverse
#         if url.startswith('/'):
#             return self.driver.get('{}{}{}'.format(
#                 self.live_server_url,
#                 url.rstrip('/'),
#                 '/' if '?' not in url else ''), *args, **kwargs)
#         return self.driver.get('{}{}'.format(
#             self.live_server_url, reverse(url, args=args, kwargs=kwargs)))
#
#     def create_pre_authenticated_session(self, user=None):
#         user = user or self.user
#         from django.contrib.sessions.backends.db import SessionStore
#         from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
#         from django.conf import settings
#         session = SessionStore()
#         session[SESSION_KEY] = user.pk
#         session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
#         session.save()
#         # to set a cookie we need fo first visit the domain.
#         # 404 pages load the quicktest! If is in testing of Mezzanine (>=3.1.9)
#         # use an "admin" for bug on template_tags of mezzanine if app 'blog'
#         # is not installed.
#         self.driver.get(
#             '{}/admin/404_no_such_url/'.format(self.live_server_url))
#         self.driver.add_cookie(dict(name=settings.SESSION_COOKIE_NAME,
#                                     value=session.session_key,
#                                     path='/'))
#         return session.session_key
#
#     @classmethod
#     def setUpClass(cls):
#         cls.driver = WebDriver()
#         super(MySeleniumTests, cls).setUpClass()
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.driver.quit()
#         super(MySeleniumTests, cls).tearDownClass()
#
#     def setUp(self):
#         self.user = requester()
#         self.create_pre_authenticated_session()
#
#     def test_login(self):
#         # pytest.set_trace()
#         from ..conftest import get_tipologies
#         tipologies = get_tipologies(2)
#         self.get(admin_urlname(Ticket._meta, 'add'))
#         for t in tipologies:
#             self.driver.find_element_by_css_selector(
#                 "#id_tipologies_from option[value='{}']".format(t.pk)).click()
#             self.driver.find_element_by_css_selector(
#                 '#id_tipologies_add_link').click()
#         script = "tinyMCE.activeEditor.setContent('{}');".format("foo")
#         self.driver.execute_script(script)
#         self.driver.find_element_by_css_selector(
#             "#id_priority input[value='{}']".format(PRIORITY_NORMAL)).click()
#         self.driver.find_element_by_name('_save').click()
#         ticket = Ticket.objects.latest()
#         self.assertEqual(ticket.requester_id, self.user.id)
#         self.assertEqual(ticket.priority, PRIORITY_NORMAL)
#         self.assertIn("foo", ticket.content)
#         self.assertSetEqual(
#             set(ticket.tipologies.values_list('pk', flat=True)),
#             {t.pk for t in tipologies})
#
#         # print(self.user.user)
#
