# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest


WINDOW_SIZE = (1024, 768)


@pytest.fixture(scope='session')
def display(request):
    try:
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=WINDOW_SIZE)
        display.start()

        def fin():
            display.stop()

        request.addfinalizer(fin)
        return display
    except ImportError:
        pass
    except Exception as e:
        print("Error with pyvirtualdisplay.Display: {}".format(str(e)))
    return None


class LiveBrowser(object):

    def __init__(self, driver, live_server, user=None):
        length_implicitly_wait = 30
        self.driver = driver
        self.live_server = live_server
        self.driver.set_window_size(*WINDOW_SIZE)
        # if 'TRAVIS' in os.environ and os.environ['TRAVIS']:
        #     length_implicitly_wait = 20
        self.driver.implicitly_wait(length_implicitly_wait)
        self.user = user

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    def quit(self):
        self.driver.quit()

    @property
    def current_url(self):
        return self.driver.current_url.replace(self.live_server.url, '')

    def get(self, url, *args, **kwargs):
        from django.core.urlresolvers import reverse
        if url.startswith('/'):
            return self.driver.get('{}{}{}'.format(
                self.live_server.url,
                url.rstrip('/'),
                '/' if '?' not in url else ''), *args, **kwargs)
        return self.driver.get('{}{}'.format(
            self.live_server.url, reverse(url, args=args, kwargs=kwargs)))

    def create_pre_authenticated_session(self, user):
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
        from django.conf import settings
        self.user = user
        session = SessionStore()
        session[SESSION_KEY] = self.user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        # to set a cookie we need fo first visit the domain.
        # 404 pages load the quicktest! If is in testing of Mezzanine (>=3.1.9)
        # use an "admin" for bug on template_tags of mezzanine if app 'blog'
        # is not installed.
        self.driver.get(
            '{}/admin/404_no_such_url/'.format(self.live_server.url))
        self.driver.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
        ))
        return session.session_key


class MezzanineLiveBrowser(LiveBrowser):
    def set_content_to_tinymce(self, content=''):
        """
        Set content of tinyMCE.

        :param content: text to set at content of tinyMCE
        :return:
        """
        script = "tinyMCE.activeEditor.setContent('{}');".format(content)
        return self.driver.execute_script(script)

    def get_messages(self, level=None):
        selector = '.messagelist li'
        if level:
            selector += '.{}'.format(level)
        return self.driver.find_elements_by_css_selector(selector)


@pytest.fixture
def browser(request, live_server):
    from selenium import webdriver
    driver = webdriver.Firefox()
    live_browser = MezzanineLiveBrowser(driver, live_server)

    def fin():
        live_browser.quit()

    request.addfinalizer(fin)
    return live_browser


@pytest.fixture
def browser_r(browser, requester):
    browser.create_pre_authenticated_session(requester)
    return browser
