# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from selenium import webdriver

try:
    from pyvirtualdisplay import Display
except ImportError:
    pass


class FunctionalTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.display = None
        try:
            display = Display(visible=0, size=(1024, 768))
            display.start()
        except:
            pass
        cls.browser = webdriver.Firefox()
        cls.browser.set_window_size(1024, 768)
        cls.browser.implicitly_wait(5)
        super(FunctionalTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        if cls.display:
            cls.display.stop()
        super(FunctionalTest, cls).tearDownClass()

    def tearDown(self):
        if self.display:
            time.sleep(1)

    def get_url(self, url, args=None, kwargs=None):
        if url.startswith('/'):
            return '%s%s/' % (self.live_server_url, url.rstrip('/'))
        return '%s%s' % (self.live_server_url,
                         reverse(url, args=args, kwargs=kwargs))

    def create_pre_authenticated_session(self, user):
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        # to set a cookie we need fo first visit the domain.
        # 404 pages load the quicktest!
        self.browser.get('{0}/404_no_such_url/'.format(self.live_server_url))
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
        ))
        return session.session_key
