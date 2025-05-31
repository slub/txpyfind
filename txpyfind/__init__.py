"""
With ``txpyfind`` you can access data exports from TYPO3-find.
"""
from ._version import __version__, version, version_tuple
from . import client, parser

__all__ = ["__version__", "version", "version_tuple", "client", "parser"]
