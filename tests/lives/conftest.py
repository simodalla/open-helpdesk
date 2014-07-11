# -*- coding: utf-8 -*-
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

@pytest.fixture(scope='module')
def display(request):
    try:
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1024, 768))
        display.start()

        def fin():
            print("finalizing pyvirtualdisplay...")
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
        self.driver = driver
        self.live_server = live_server
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(5)
        self.user = user

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    def quit(self):
        self.driver.quit()

    def get(self, url, *args, **kwargs):
        from django.core.urlresolvers import reverse
        if url.startswith('/'):
            return self.driver.get('{}{}/'.format(
                self.live_server.url, url.rstrip('/')), *args, **kwargs)
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
        # 404 pages load the quicktest!
        self.driver.get('{}/404_no_such_url/'.format(self.live_server.url))
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


@pytest.fixture(scope='module')
def browser(request, display, live_server):
    print('starting firefox webdriver...')
    from selenium import webdriver
    driver = webdriver.Firefox()
    live_browser = MezzanineLiveBrowser(driver, live_server)

    def fin():
        print('finalizing firefox webdriver...')
        live_browser.quit()

    request.addfinalizer(fin)
    return live_browser


@pytest.fixture
def browser_r(browser, requester):
    browser.create_pre_authenticated_session(requester)
    return browser
