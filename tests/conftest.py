
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from six.moves import cStringIO



@pytest.fixture(scope='module')
def stringios():
    return cStringIO(), cStringIO()


@pytest.fixture(scope="class")
def helpdesker(request):
    helpdesker_conf = (getattr(request.cls, 'helpdesker_conf', None)
                       or getattr(request.module, 'helpdesker_conf', None))
    if not helpdesker_conf:
        return None
    import helpdesk.defaults
    from tests.factories import UserFactory, GroupFactory
    helpdesker_conf = getattr(helpdesk.defaults, helpdesker_conf, None)
    if not helpdesker_conf:
        return None
    request.cls.user = UserFactory(
        groups=[GroupFactory(name=helpdesker_conf[0],
                             permissions=list(helpdesker_conf[1]))])


@pytest.fixture(scope='module')
def requester():
    from tests.factories import UserFactory, GroupFactory
    from helpdesk.defaults import HELPDESK_REQUESTERS
    user = UserFactory(groups=[GroupFactory(name=HELPDESK_REQUESTERS[0])],
                       permissions=list(HELPDESK_REQUESTERS[1]))
    return user


@pytest.fixture(scope="class")
def helpdesker_live(request, helpdesker):
    from django.contrib.sites.models import Site
    from mezzanine.core.models import SitePermission
    from .settings import SITE_ID
    sp = SitePermission.objects.create(user=request.cls.user)
    sp.sites.add(Site.objects.get(pk=SITE_ID))
    # request.cls.user = request.cls.user


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

    def create_pre_authenticated_session(self):
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
        from django.conf import settings
        session = SessionStore()
        session[SESSION_KEY] = self.user.pk
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


@pytest.fixture(scope="class")
def browser(request, display, live_server):
    from selenium import webdriver
    driver = webdriver.Firefox()
    live_browser = LiveBrowser(driver, str(live_server))

    def fin():
        print("finalizing firefox webdriver...")
        live_browser.quit()

    request.addfinalizer(fin)
    request.cls.browser = browser


@pytest.fixture(scope="class")
def authenticated_browser(request, browser, helpdesker_live):
    browser.user = request.cls.user
    browser.create_pre_authenticated_session()
    request.cls.browser = browser