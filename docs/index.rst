.. include:: ../README.rst
   :end-before: About

.. include:: ../README.rst
   :start-after: =====
   :end-before: Features

Features:

.. include:: ../README.rst
   :start-line: 35
   :end-before: Useful links


Configuration
=============

.. automodule:: reana_db.config
   :members:


API
===

Database management
-------------------

.. automodule:: reana_db.database
   :members:

Models
------

.. automodule:: reana_db.models
   :members:

Utilities
---------

.. automodule:: reana_db.utils
   :members:


CLI API
=======

.. click:: reana_db.cli:cli
   :prog: reana-db
   :show-nested:

.. include:: ../CHANGES.rst

.. include:: ../CONTRIBUTING.rst


License
=======

.. include:: ../LICENSE

In applying this license, CERN does not waive the privileges and immunities
granted to it by virtue of its status as an Intergovernmental Organization or
submit itself to any jurisdiction.

.. include:: ../AUTHORS.rst
