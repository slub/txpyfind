"""Python client for querying TYPO3-find (Solr-based search) instances."""
from ._version import __version__, version, version_tuple
from . import client, parser

__all__ = ["__version__", "version", "version_tuple", "client", "parser"]
