Installation
============
The easiest method is to install directly from pypi using `pip: http://www.pip-installer.org/` by
running the command below, which will also install the required
dependencies mentioned above::

    $ pip install open-helpdesk

If you prefer, you can download openhelpdesk and install it directly from
source::

    $ python setup.py install

If you don't have already an configurated Mezzanine projects, the command
``mezzanine-project`` can be used to create a new Mezzanine project in similar
fashion to ``django-admin.py``::

    $ mezzanine-project project_name
    $ cd project_name
    $ python manage.py createdb --noinput


Add ``openhelpdesk`` to your ``INSTALLED_APPS`` setting before all
mezzanine apps::

    INSTALLED_APPS = (
        # ...
        'openhelpdesk',
        'mezzanine.boot',
        'mezzanine.conf',
        'mezzanine.core',
        # ...
    )

You will then want to create the necessary tables. If you are using `South http://south.aeracode.org/`
for schema migrations, you'll want to::

    $ python manage.py migrate openhelpdesk

