from txpyfind.client import Find

def test_get_document():
   # create Find instance
   slub_find = Find("https://katalog.slub-dresden.de", document_path="id", export_format="json-ld")
   # retrieve JSON-LD data (detail view)
   slub_ld_doc = slub_find.get_document("0-1132486122")
   assert slub_ld_doc is not None
   assert '@graph' in slub_ld_doc.raw
   assert any(slub_ld_doc.raw['@graph'])
   assert '@id' in slub_ld_doc.raw['@graph'][0]
   assert 'katalog.slub-dresden.de' in slub_ld_doc.raw['@graph'][0]['@id']

def test_get_query():
   # create Find instance
   slub_find = Find("https://katalog.slub-dresden.de", document_path="id", export_format="json-ld")
   # retrieve JSON-LD data (query view)
   slub_ld_doc = slub_find.get_query("manfred bonitz")
   assert slub_ld_doc is not None
   assert '@graph' in slub_ld_doc.raw
   assert any(slub_ld_doc.raw['@graph'])
   assert '@id' in slub_ld_doc.raw['@graph'][0]

def test_get_query_via_url():
   # create Find instance
   slub_find = Find("https://katalog.slub-dresden.de", document_path="id", export_format="json-ld")
   # retrieve JSON-LD data (query view)
   slub_ld_doc = slub_find.get_query_via_url("https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz")
   assert slub_ld_doc is not None
   assert '@graph' in slub_ld_doc.raw
   assert any(slub_ld_doc.raw['@graph'])
   assert '@id' in slub_ld_doc.raw['@graph'][0]

def test_pagination():
   # create Find instance
   slub_find = Find("https://katalog.slub-dresden.de", document_path="id")
   # scroll SOLR JSON data (query view + pagination)
   slub_solr_docs = slub_find.scroll_get_query("manfred bonitz", batch=10)
   assert slub_solr_docs is not None
   assert len(slub_solr_docs) > 0
   # stream SOLR JSON data (query view + pagination)
   slub_solr_docs2 = slub_find.stream_get_query("manfred bonitz", batch=10)
   assert slub_solr_docs2 is not None
   slub_solr_docs2 = list(slub_solr_docs2)
   assert len(slub_solr_docs2) > 0
   assert len(slub_solr_docs) == len(slub_solr_docs2)
