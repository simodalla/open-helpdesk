# -*- coding: utf-8 -*-
import pytest


def pytest_addoption(parser):
    parser.addoption('--livetest', action='store_true',
                     help='run live tests')


def pytest_runtest_setup(item):
    if ('livetest' in item.keywords and
            not item.config.getoption('--livetest')):
        pytest.skip('need --livetest option to run')
