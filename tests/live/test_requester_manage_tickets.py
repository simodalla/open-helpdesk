# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

pytestmark = pytest.mark.django_db
# helpdesker_conf = 'HELPDESK_REQUESTERS'


@pytest.mark.usefixtures("authenticated_browser")
class TestRequesterManageTickets(object):

    helpdesker_conf = 'HELPDESK_OPERATORS'

    # def test_live_server(self, authenticated_browser):
    #     browser, user = authenticated_browser
    #     browser.get('/admin/helpdesk/')
    def test_live_server(self):
        print(self.browser)
        print(id(self.browser.user))
        print(self.browser.user.sitepermissions.all())
        print(self.browser.user.groups.all())

    def test_live_server_3(self):
        print(self.browser)
        print(id(self.browser.user))
        print(self.browser.user.sitepermissions.all())
        print(self.browser.user.groups.all())


# def test_live_server_2(helpdesker):
#         print(helpdesker.groups.all())