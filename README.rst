========
txpyfind
========

``txpyfind`` enables access to data exports from `TYPO3-find <https://github.com/subugoe/typo3-find>`_
in Python. Details on the TYPO3-find setup required for data exports can be found in the section
`Data export <https://github.com/subugoe/typo3-find#data-export>`_ in the README file of that repository.

The three JSON formats ``json-all``, ``json-solr-results`` and ``raw-solr-response`` are already available
in the TYPO3 extension, see the
`partials <https://github.com/subugoe/typo3-find/tree/main/Resources/Private/Partials/Formats>`_ used
to create the three formats.

You can use the client class available in this Python package to query these exports. A simple parser
for the returned JSON objects is also available.

Installation
============

... via PyPI
~~~~~~~~~~~~

.. code-block:: bash

   pip install txpyfind

... or from GitHub source
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install git+https://github.com/slub/txpyfind.git


Command-Line Usage
==================

After installation, the ``txpyfind`` command is available (also via ``python -m txpyfind``).

Query
~~~~~

Execute a search query:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de query "manfred bonitz"

With a facet filter and pagination:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de query "python" --facet format_de14="Book, E-Book" --page 1 --count 10

Multiple ``--facet`` options can be combined:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de query "python" --facet format_de14="Book, E-Book" --facet language=German

Document
~~~~~~~~

Fetch a single document by ID:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --document-path id document 0-1132486122

Scroll
~~~~~~

Fetch all results for a query:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de scroll "manfred bonitz" --batch 10

Stream results as JSONL (one JSON object per line), useful for piping:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de scroll "manfred bonitz" --stream | jq .id

Show Request URL
~~~~~~~~~~~~~~~~

Use ``--show-url`` to print the request URL instead of fetching the response.
This works with all subcommands:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --show-url query "python" --facet format_de14="Book, E-Book"
   txpyfind --url https://katalog.slub-dresden.de --document-path id --show-url document 0-1132486122
   txpyfind --url https://katalog.slub-dresden.de --show-url scroll "python" --batch 10

Environment Variable
~~~~~~~~~~~~~~~~~~~~

Set ``TXPYFIND_URL`` to avoid repeating the ``--url`` option:

.. code-block:: bash

   export TXPYFIND_URL=https://katalog.slub-dresden.de
   txpyfind query "manfred bonitz"
   txpyfind --document-path id document 0-1132486122

Python Usage Example
====================

.. code-block:: python

   from txpyfind.client import Find
   # create Find instance
   slub_find = Find("https://katalog.slub-dresden.de", document_path="id", export_format="json-ld")
   # retrieve JSON-LD data (detail view)
   slub_ld_doc = slub_find.get_document("0-1132486122")
   # retrieve JSON-LD data (query view)
   slub_ld_q_default = slub_find.get_query("manfred bonitz")
   # query with a single facet (dict)
   slub_find.get_query("python", facet={"format_de14": "Book, E-Book"})
   # query with multiple facets (list of dicts)
   slub_find.get_query("python", facet=[{"format_de14": "Book, E-Book"}, {"language": "German"}])

See `slubfind <https://github.com/slub/slubfind>`_ for a full setup example.

License
=======

This project is licensed under the GNU General Public License v3 (GPLv3).
See the `LICENSE <LICENSE>`_ file for the full license text.
