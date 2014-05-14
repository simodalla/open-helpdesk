# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from mezzanine.core.managers import CurrentSiteManager, SearchableManager


class HeldeskableManager(CurrentSiteManager, SearchableManager):
    """
    Manually combines ``CurrentSiteManager``, and ``SearchableManager`` for
    the ``Issue`` model.
    """
    pass
