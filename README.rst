========
txpyfind
========

``txpyfind`` enables access to data exports from TYPO3-find in Python. Details on the TYPO3-find setup required for data exports can be found in the section `Data export <https://github.com/subugoe/typo3-find#data-export>`_ in the README file of the repository. The three JSON formats ``json-all``, ``json-solr-results`` and ``raw-solr-response`` are already available in the TYPO3 extension, see the `partials <https://github.com/subugoe/typo3-find/tree/main/Resources/Private/Partials/Formats>`_ used to create the three formats. You can use the client class available in this Python package to query these exports. A simple parser for the returned JSON objects is also available.

Installation
============

... via SSH
~~~~~~~~~~~

.. code-block:: bash

   pip install -e git+ssh://git@github.com/herreio/txpyfind.git#egg=txpyfind

... or via HTTPS
~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e git+https://github.com/herreio/txpyfind.git#egg=txpyfind


Usage Example
=============

.. code-block:: python

   from txpyfind.client import Find
   # create Find instance
   slub_find = Find("https://katalog.slub-dresden.de", document_path="id", export_format="json-ld")
   # retrieve JSON-LD data (detail view)
   slub_ld_doc = slub_find.get_document("0-1132486122")
   # retrieve JSON-LD data (query view)
   slub_ld_q_default = slub_find.get_query("manfred bonitz")
   # ...
