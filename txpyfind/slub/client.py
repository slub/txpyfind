from . import parser
from ..client import Find


class SlubFind(Find):

    def __init__(self, base_url="https://katalog.slub-dresden.de",
                 document_path="id", export_format="app",
                 export_page=1369315142):
        super().__init__(base_url, document_path=document_path,
                         export_format=export_format, export_page=export_page)

    def app_details(self, document_id):
        return self.get_document(document_id, data_format="app", parser_class=parser.AppDetails)
