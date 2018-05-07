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


Package Documentation
---------------------

.. automodule:: bob.db.swan
.. automodule:: bob.db.swan.query_bio
.. automodule:: bob.db.swan.query_pad
