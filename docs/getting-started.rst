Getting Started
===============

OpenHelpdesk required an configurated ``Mezzanine`` project.

.. _no_mezzanine_prj:

You don't have an existing Mezzanine projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command ``mezzanine-project`` can be used to create a new `Mezzanine`_ project in similar
fashion to ``django-admin.py``::

    $ mezzanine-project open-helpdesk-prj
    $ cd open-helpdesk-prj

Add ``openhelpdesk`` and ``autocomplete_light`` to your ``INSTALLED_APPS``
setting into your ``settings.py`` before all mezzanine apps::

    INSTALLED_APPS = (
        # ...
        "openhelpdesk",
        "autocomplete_light",
        "mezzanine.boot",
        "mezzanine.conf",
        "mezzanine.core",
        # ...
    )

You will then want to create the necessary tables::

    $ python manage.py createdb --noinput

.. note::

    The ``createdb`` command is a shortcut for using Django's ``syncdb``
    command and setting the initial migration state for `South`_. You
    can alternatively use ``syncdb`` and ``migrate`` if preferred.
    South is automatically added to INSTALLED_APPS if the
    ``USE_SOUTH`` setting is set to ``True``.


You have already an existing Mezzanine projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ cd existing_project_name

Add ``openhelpdesk`` and ``autocomplete_light`` to your ``INSTALLED_APPS``
setting into your ``settings.py`` before all mezzanine apps::

    INSTALLED_APPS = (
        # ...
        "openhelpdesk",
        "autocomplete_light",
        "mezzanine.boot",
        "mezzanine.conf",
        "mezzanine.core",
        # ...
    )

You will then want to create the necessary tables. If you are using
`South`_ for schema migrations, you'll want to::

    $ python manage.py migrate openhelpdesk

otherwise you, you'll want to::


    $ python manage.py syncdb


Configure ``autocompleting`` functionality
------------------------------------------

OpenHelpdesk use `autocomplete_light
<https://pypi.python.org/pypi/django-autocomplete-light/>`_ to provide autocompleting.

In ``urls.py``, call ``autocomplete_light.autodiscover()`` before
``admin.autodiscover()`` **and before any import of a form with
autocompletes**. It might look like this:

.. code-block:: python

    import autocomplete_light
    autocomplete_light.autodiscover()

    import admin
    admin.autodiscover()

Install the autocomplete view in ``urls.py`` using the `include function
<https://docs.djangoproject.com/en/dev/topics/http/urls/#including-other-urlconfs>`_.
*before* ``Mezzanine`` urls:

.. code-block:: python

    # MEZZANINE'S URLS
    # ----------------
    # ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
    # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
    # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
    # WILL NEVER BE MATCHED!
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    # If you'd like more granular control over the patterns in
    # ``mezzanine.urls``, go right ahead and take the parts you want
    # from it, and use them directly below instead of using
    # ``mezzanine.urls``.
    ("^", include("mezzanine.urls")),

Initialization
--------------

Use ``inithelpdesk`` for creating required data, groups, and permission by ``OpenHelpdesk``::

    $ python manage.py inithelpdesk
    $ python manage.py runserver

You should then be able to browse to http://127.0.0.1:8000/admin/ and
log in using your account if the default account (``username: admin, password:
default``). If you'd like to specify a different username and password
during set up, simply exclude the ``--noinput`` option included above
when running ``createdb``. If you already have an existing project log in
with your superuser account.

.. GENERAL LINKS

.. _`Mezzanine`: http://mezzanine.jupo.org
.. _`South`: http://south.aeracode.org/