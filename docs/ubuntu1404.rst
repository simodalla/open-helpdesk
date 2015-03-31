======================================================
Configure Ubuntu 14.04 for OpenHelpdesk's installation
======================================================

This guide will drive you to configure an ``Ubuntu 14.04`` (server) for
afterwards installation an OpenHelpdesk instance.
Subsequent commands will be launched as ``root`` user.

Pip and setuptools
------------------

Install last version of `pip`_ and ``setuptools``::

    # wget https://bootstrap.pypa.io/get-pip.py
    # python get-pip.py

Virtualen and virtualenwrapper
------------------------------
Install last version of ``virtualenv`` and ``virtualenvwrapper``::

    # pip install virtualenv virtualenvwrapper
    # mkdir /opt/virtualenvs
    # mkdir /opt/djangoprjs

and configure ``virtualenvwrapper`` adding three lines to your shell startup file (``.bashrc``, ``.profile``,
etc.)::


    export WORKON_HOME=/opt/virtualenvs
    export PROJECT_HOME=/opt/djangoprjs
    source /usr/local/bin/virtualenvwrapper.sh

After editing it, reload the startup file (e.g., run ``source
~/.bashrc``).

.. note::

    view the `Virtualenvwrapper Docs`_ for more information

Packages required
-----------------

Install ``libpq-dev`` and ``python-dev`` packages::


    # apt-get install -y libpq-dev python-dev

Virtuaenv for OpenHelpdesk
--------------------------
Create a virtualenv named ``open-helpdesk`` for OpenHelpdesk instance::

    # root@ubuntu140402:~# mkvirtualenv open-helpesk

Installation
------------

Activate ``open-helpdesk`` virtualenv::

    # workon openhelpdesk

and install into it ``OpenHelpdesk`` from pypi using ``pip`` by
running the command below, which will also install the required
dependencies::

    (open-helpesk)# pip install open-helpdesk

Move into ``/opt/djangoprjs``::

    (open-helpesk)# cd /opt/djangoprjs

and follow the paragraph :ref:`You don't have an existing Mezzanine projects <no_mezzanine_prj>`
into :doc:`Getting Started <getting-started>` section.


.. GENERAL LINKS

.. _`pip`: https://pip.pypa.io/en/latest/installing.html#install-pip
.. _`Virtualenvwrapper Docs`: https://virtualenvwrapper.readthedocs.org/en/latest/install.html