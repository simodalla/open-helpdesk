# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope='session')
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
                self.live_server, url.rstrip('/')), *args, **kwargs)
        return self.driver.get('{}{}'.format(
            self.live_server, reverse(url, args=args, kwargs=kwargs)))

    def create_pre_authenticated_session(self, user):
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
        from django.conf import settings
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        # to set a cookie we need fo first visit the domain.
        # 404 pages load the quicktest!
        self.driver.get('{0}/404_no_such_url/'.format(self.live_server))
        self.driver.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
        ))
        return session.session_key

    def set_content_to_tinymce(self, content=''):
        """
        Set content of tinyMCE.

        :param content: text to set at content of tinyMCE
        :return:
        """
        script = "tinyMCE.activeEditor.setContent('{}');".format(content)
        return self.driver.execute_script(script)


@pytest.fixture(scope='module')
def browser(request, display, live_server):
    from selenium import webdriver
    driver = webdriver.Firefox()
    live_browser = LiveBrowser(driver, str(live_server))

    def fin():
        print('finalizing firefox webdriver...')
        live_browser.quit()

    request.addfinalizer(fin)
    return live_browser


@pytest.fixture
def browser_requestered(browser, requester):
    browser.create_pre_authenticated_session(requester)
    return browser, requester
