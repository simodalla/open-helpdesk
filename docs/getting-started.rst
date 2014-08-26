Getting Started
===============

OpenHelpdesk required an configurated ``Mezzanine`` project.

You don't have an existing Mezzanine projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command ``mezzanine-project`` can be used to create a new `Mezzanine`_ project in similar
fashion to ``django-admin.py``::

    $ mezzanine-project project_name
    $ cd project_name

Add ``openhelpdesk`` to your ``INSTALLED_APPS`` setting into ``settings.py``
before all ``Mezzanine`` apps::

    INSTALLED_APPS = (
        # ...
        'openhelpdesk',
        'mezzanine.boot',
        'mezzanine.conf',
        'mezzanine.core',
        # ...
    )

You will then want to create the necessary tables::

    $ cd project_name
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

Add ``openhelpdesk`` to your ``INSTALLED_APPS`` setting into your ``settings.py``
before all mezzanine apps::

    INSTALLED_APPS = (
        # ...
        'openhelpdesk',
        'mezzanine.boot',
        'mezzanine.conf',
        'mezzanine.core',
        # ...
    )

You will then want to create the necessary tables. If you are using
`South`_ for schema migrations, you'll want to::

    $ python manage.py migrate openhelpdesk

otherwise you, you'll want to::


    $ python manage.py syncdb

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