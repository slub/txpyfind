"""
Offline unit tests for txpyfind.parser classes.
"""
import json
import pytest
from txpyfind.parser import (
    JSONResponse,
    RawSolrResponse,
    SolrResultsResponse,
    AllResponse,
)


# --- JSONResponse ---

class TestJSONResponse:

    def test_valid_dict(self):
        data = {"key": "value", "count": 42}
        r = JSONResponse(json.dumps(data))
        assert r.raw == data
        assert r.fields == ["key", "count"]

    def test_valid_list(self):
        data = [{"a": 1}, {"b": 2}]
        r = JSONResponse(json.dumps(data))
        assert r.raw == data
        assert r.fields == []

    def test_invalid_json(self):
        r = JSONResponse("not json")
        assert r.raw is None
        assert r.fields == []

    def test_html_unescaping(self):
        data = {"title": "foo &amp; bar"}
        r = JSONResponse(json.dumps(data))
        assert r._field("title") == "foo & bar"

    def test_html_unescaping_list(self):
        data = {"tags": ["a &amp; b", "c &lt; d"]}
        r = JSONResponse(json.dumps(data))
        assert r._field("tags") == ["a & b", "c < d"]


# --- RawSolrResponse ---

class TestRawSolrResponse:

    def _make(self, response=None, **extra):
        data = {}
        if response is not None:
            data["response"] = response
        data.update(extra)
        return RawSolrResponse(json.dumps(data))

    def test_valid_response(self):
        docs = [{"id": "1"}, {"id": "2"}]
        r = self._make(response={"numFound": 2, "start": 0, "docs": docs})
        assert r.ok is True
        assert r.num_found == 2
        assert r.start == 0
        assert r.docs == docs

    def test_missing_response_key(self):
        r = RawSolrResponse(json.dumps({"other": "data"}))
        assert r.ok is False
        assert r.num_found == 0
        assert r.docs == []

    def test_empty_docs(self):
        r = self._make(response={"numFound": 0, "start": 0, "docs": []})
        assert r.ok is True
        assert r.num_found == 0
        assert r.docs == []

    def test_facet_counts(self):
        facets = {"facet_fields": {"type": ["book", 10]}}
        r = self._make(
            response={"numFound": 0, "start": 0, "docs": []},
            facet_counts=facets)
        assert r.facet_counts == facets

    def test_facet_counts_missing(self):
        r = self._make(response={"numFound": 0, "start": 0, "docs": []})
        assert r.facet_counts is None

    def test_highlighting(self):
        hl = {"doc1": {"title": ["<em>test</em>"]}}
        r = self._make(
            response={"numFound": 0, "start": 0, "docs": []},
            highlighting=hl)
        assert r.highlighting == hl

    def test_highlighting_missing(self):
        r = self._make(response={"numFound": 0, "start": 0, "docs": []})
        assert r.highlighting is None

    def test_raw_and_fields_available(self):
        r = self._make(response={"numFound": 0, "start": 0, "docs": []})
        assert isinstance(r.raw, dict)
        assert "response" in r.fields


# --- SolrResultsResponse ---

class TestSolrResultsResponse:

    def test_valid_list(self):
        data = [{"id": "1", "title": "A"}, {"id": "2", "title": "B"}]
        r = SolrResultsResponse(json.dumps(data))
        assert r.ok is True
        assert r.docs == data

    def test_empty_list(self):
        r = SolrResultsResponse(json.dumps([]))
        assert r.ok is True
        assert r.docs == []

    def test_non_list_input(self):
        r = SolrResultsResponse(json.dumps({"key": "value"}))
        assert r.ok is False
        assert r.docs == []


# --- AllResponse ---

class TestAllResponse:

    def test_valid_with_settings(self):
        data = {"settings": {"lang": "de"}, "other": "x"}
        r = AllResponse(json.dumps(data))
        assert r.ok is True
        assert r.settings == {"lang": "de"}

    def test_missing_settings(self):
        r = AllResponse(json.dumps({"other": "data"}))
        assert r.ok is True
        assert r.settings is None

    def test_non_dict_input(self):
        r = AllResponse(json.dumps([1, 2, 3]))
        assert r.ok is False
        assert r.settings is None
