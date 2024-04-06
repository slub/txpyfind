========
txpyfind
========

``txpyfind`` allows to access data exports from TYPO3-find in Python. For details regarding the TYPO3-find setup needed to have data exports, see the section on `data exports <https://github.com/subugoe/typo3-find#data-export>`_  in the README file of the repository. The three JSON formats ``json-all``, ``json-solr-results`` and ``raw-solr-response`` are already available in the TYPO3 extension, but can be extended. See the `partials <https://github.com/subugoe/typo3-find/tree/main/Resources/Private/Partials/Formats>`_ used to create the three formats mentioned above. With the client class available in this Python package, you can query those exports. A simple parser for JSON objects returned is also available.

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
