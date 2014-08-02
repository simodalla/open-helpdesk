# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.test import LiveServerTestCase

from selenium.webdriver.firefox.webdriver import WebDriver


pytestmark = pytest.mark.django_db


@pytest.mark.livetest
class MySeleniumTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))