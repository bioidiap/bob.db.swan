.. vim: set fileencoding=utf-8 :

.. _bob.db.swan:

==================================
 SWAN Database Access API for Bob
==================================

To use this database, you may need to download additional files:

.. code-block:: sh

	$ bob_dbmanage.py swan download --missing
	
To configure the location of the database on your computer:

.. code-block:: sh

    $ bob config set bob.db.swan.directory /path/to/swan/database


Package Documentation
---------------------

.. automodule:: bob.db.swan
.. automodule:: bob.db.swan.query
.. automodule:: bob.db.swan.models
