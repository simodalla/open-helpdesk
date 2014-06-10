# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.contrib.auth.models import Group
from django.core.management import call_command

from helpdesk.defaults import (
    HELPDESK_REQUESTERS, HELPDESK_OPERATORS, HELPDESK_ADMINS)


@pytest.mark.django_db
def test_call_initihelpsedk_command(stringios):
    stdout, stderr = stringios
    call_command('inithelpdesk', stdout=stdout, stderr=stderr)
    groups_data = {t[0]: t[1] for t in (HELPDESK_REQUESTERS,
                                        HELPDESK_OPERATORS,
                                        HELPDESK_ADMINS)}
    groups = Group.objects.all()
    assert len(groups) == len(groups_data)
    assert (
        set(groups.values_list('name', flat=True)) ==
        set(groups_data.keys()))
    for group in groups:
        assert (set(group.permissions.values_list('codename', flat=True)) ==
                set([p.split('.')[1] for p in groups_data[group.name]
                     if p.startswith('helpdesk')]))