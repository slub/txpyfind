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
