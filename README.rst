========
txpyfind
========

``txpyfind`` is a Python client and CLI for querying
`TYPO3-find <https://github.com/subugoe/typo3-find>`_
(Solr-based search) instances. It builds URLs with
TYPO3-find-specific query parameters, fetches responses,
and parses them.

Three parser classes are included for the native
TYPO3-find data formats: ``RawSolrResponse``
(``raw-solr-response``), ``SolrResultsResponse``
(``json-solr-results``), and ``AllResponse``
(``json-all``). Custom parser classes can be passed
to the client for any other format. The plain response
text is always available via the ``.plain`` attribute.

See `slubfind <https://github.com/slub/slubfind>`_
for a real-world implementation with custom query
types and instance-specific response parsing.

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

Query Type
~~~~~~~~~~

Use ``--type`` to select a query type (e.g. ``author``, ``title``). Valid
values depend on the TYPO3-find instance. Use ``--query-type`` (repeatable)
to whitelist the types accepted by ``--type``; if omitted, only ``default``
is allowed:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de query --query-type default --query-type author --query-type title --type author "bonitz"

Document
~~~~~~~~

Fetch a single document by ID:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de document --document-path id --export-format json-ld 0-1132486122

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

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --show-url document --document-path id --export-format json-ld 0-1132486122

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --show-url scroll "python" --batch 10

Export Format
~~~~~~~~~~~~~

Use ``--export-format`` on the ``query`` subcommand to select the response
format (default: ``raw-solr-response``). On the ``document`` subcommand,
``--export-format`` is required and has no default. The three formats built
into TYPO3-find are ``raw-solr-response``, ``json-all``, and
``json-solr-results``, but any format string accepted by the instance can
be used:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de query --export-format json-solr-results "manfred bonitz"

Plain Output
~~~~~~~~~~~~

Use ``--plain`` to print the raw response text instead of parsed JSON output.
This works with the ``query`` and ``document`` subcommands:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --plain query "manfred bonitz"

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --plain document --document-path id --export-format json-ld 0-1132486122

Custom Parser
~~~~~~~~~~~~~

Use ``--parser`` to load a custom parser class by its dotted import path.
This allows packages built on top of ``txpyfind`` (like ``slubfind``) to
use their own response parsing from the CLI. The class must accept a plain
text string as its constructor argument and provide a ``.raw`` attribute
with JSON-serializable data (and a ``.plain`` attribute for ``--plain``).
Use ``--parser none`` to disable parsing entirely and print the raw
response text:

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --parser slubfind.parser.FincSolrResponse query "manfred bonitz"

.. code-block:: bash

   txpyfind --url https://katalog.slub-dresden.de --parser none query "manfred bonitz"

Environment Variable
~~~~~~~~~~~~~~~~~~~~

Set ``TXPYFIND_URL`` to avoid repeating the ``--url`` option:

.. code-block:: bash

   export TXPYFIND_URL=https://katalog.slub-dresden.de

.. code-block:: bash

   txpyfind query "manfred bonitz"

.. code-block:: bash

   txpyfind document --document-path id --export-format json-ld 0-1132486122

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

   # access the plain response text
   result = slub_find.get_query("manfred bonitz")
   print(result.plain)

   # use a specific built-in parser
   from txpyfind.parser import RawSolrResponse
   result = slub_find.get_query("manfred bonitz", parser_class=RawSolrResponse)
   print(result.num_found, result.docs)

   # use a custom parser class from another package
   from slubfind.parser import FincSolrResponse
   slub_find = Find("https://katalog.slub-dresden.de", parser_class=FincSolrResponse)

License
=======

This project is licensed under the GNU General Public License v3 (GPLv3).
See the `LICENSE <LICENSE>`_ file for the full license text.
