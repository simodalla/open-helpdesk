# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import os


def pytest_configure(config):
    settings_module = "project_template.project_template.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
