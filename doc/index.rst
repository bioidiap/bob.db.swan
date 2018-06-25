.. vim: set fileencoding=utf-8 :

.. _bob.db.swan:

==================================
 SWAN Database Access API for Bob
==================================

This package provides an API to the protocols of the SWAN database.

To configure the location of the database and the location of face annotations
on your computer:

.. code-block:: sh

    $ bob config set bob.db.swan.directory /path/to/swan/database
    $ bob config set bob.db.swan.annotation_dir /path/to/swan/annotations

Documentation
-------------

.. toctree::
   :maxdepth: 2

   protocols
   py_api

