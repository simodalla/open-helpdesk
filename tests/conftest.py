
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from six.moves import cStringIO



@pytest.fixture(scope='module')
def stringios():
    return cStringIO(), cStringIO()


def helpdesker(helpdesker_conf):
    from django.contrib.sites.models import Site
    import helpdesk.defaults
    from .factories import UserFactory, GroupFactory
    from .settings import SITE_ID

    helpdesker_conf = getattr(helpdesk.defaults, helpdesker_conf, None)
    if not helpdesker_conf:
        return None
    user = UserFactory(
        groups=[GroupFactory(name=helpdesker_conf[0],
                             permissions=list(helpdesker_conf[1]))])
    sp = user.sitepermissions.create(user=user)
    sp.sites.add(Site.objects.get(pk=SITE_ID))
    return user


@pytest.fixture(scope='module')
def requester():
    return helpdesker('HELPDESK_REQUESTERS')


@pytest.fixture(scope='module')
def operator():
    return helpdesker('HELPDESK_OPERATORS')


@pytest.fixture
def rf_with_helpdeskuser(request, rf):
    rf.user = None
    if getattr(request, 'cls', None):
        class HelpdeskUser(object):
            def is_requester(self):
                return getattr(request.cls, 'is_requester', False)

            def is_operator(self):
                return getattr(request.cls, 'is_operator', False)

            def is_admin(self):
                return getattr(request.cls, 'is_admin', False)
        rf.user = HelpdeskUser()
    return rf


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


@pytest.fixture(scope='module')
def browser_requestered(browser, requester):
    print(browser, requester)
    browser.create_pre_authenticated_session(requester)
    return browser, requester