# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from selenium import webdriver

from django.contrib.auth import get_user_model

from ..conftest import requester

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.conf import settings


def create_pre_authenticated_session(driver, user, liveserver_url):
    session = SessionStore()
    session[SESSION_KEY] = user.pk
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session.save()
    # to set a cookie we need fo first visit the domain.
    # 404 pages load the quicktest! If is in testing of Mezzanine (>=3.1.9)
    # use an "admin" for bug on template_tags of mezzanine if app 'blog'
    # is not installed.
    driver.get(
        '{}/admin/'.format(liveserver_url))
    driver.add_cookie(dict(
        name=settings.SESSION_COOKIE_NAME,
        value=session.session_key,
        path='/',
    ))
    return driver


def test_live_live(live_server):
    print(get_user_model().objects.values_list('pk', flat=True))
    driver = webdriver.Firefox()
    # user = requester()
    # create_pre_authenticated_session(driver, user, live_server.url)
    print(get_user_model().objects.values_list('pk', flat=True))
    # session = SessionStore()
    # session[SESSION_KEY] = user.pk
    # session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    driver.get("http://www.python.org")
    # driver.get('{}/admin/'.format(live_server.url))
    driver.quit()


def test_live_live_1(live_server):
    print(get_user_model().objects.values_list('pk', flat=True))
    driver = webdriver.Firefox()
    # user = requester()
    # create_pre_authenticated_session(driver, user, live_server.url)
    print(get_user_model().objects.values_list('pk', flat=True))
    driver.get("http://www.python.org")
    driver.get('{}/admin/'.format(live_server.url))
    driver.quit()
