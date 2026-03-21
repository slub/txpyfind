"""
parser module of ``txpyfind`` package
"""
import html
import json
import logging


class JSONResponse:  # pylint: disable=R0903
    """
    ``JSONResponse`` class from ``txpyfind.parser`` module
    """

    def __init__(self, plain):
        self.plain = plain
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        try:
            self.raw = json.loads(plain)
        except json.decoder.JSONDecodeError as err:
            self.logger.error("Failed to parse JSON response: %s", err)
            self.raw = None
        self.fields = self._names(raw=self.raw)

    def _names(self, raw=None):
        if raw is None:
            raw = self.raw
        if isinstance(raw, dict):
            return list(raw.keys())
        return []

    def _field(self, name, raw=None):
        if raw is None:
            raw = self.raw
        if isinstance(raw, dict) and name in raw:
            return self._unescape(raw[name])
        return None

    def _unescape(self, value):
        if isinstance(value, str):
            return html.unescape(value.strip())
        if isinstance(value, list) and len(value) > 0 and \
                all(isinstance(v, str) for v in value):
            return [html.unescape(v.strip()) for v in value]
        return value


class RawSolrResponse(JSONResponse):
    """
    Parser for ``raw-solr-response`` export format.

    Expected structure::

        {"response": {"numFound": N, "start": S, "docs": [...]},
         "facet_counts": {...}, "highlighting": {...}}
    """

    def __init__(self, plain):
        super().__init__(plain)
        response = self._field("response")
        if isinstance(response, dict):
            self.ok = True
            self.num_found = response.get("numFound", 0)
            self.start = response.get("start", 0)
            self.docs = response.get("docs", [])
        else:
            self.ok = False
            self.num_found = 0
            self.start = 0
            self.docs = []

    @property
    def facet_counts(self):
        return self._field("facet_counts")

    @property
    def highlighting(self):
        return self._field("highlighting")


class SolrResultsResponse(JSONResponse):
    """
    Parser for ``json-solr-results`` export format.

    Expected structure::

        [{field1: ..., field2: ...}, ...]
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, list)

    @property
    def docs(self):
        if self.ok:
            return self.raw
        return []


class AllResponse(JSONResponse):
    """
    Parser for ``json-all`` export format.

    Expected structure::

        {"settings": {...}, ...}
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict)

    @property
    def settings(self):
        return self._field("settings")
