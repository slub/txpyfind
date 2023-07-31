from . import utils
from . import parser


class Find:

    def __init__(self, base_url, document_path=None,
                 export_format="raw-solr-response", export_page=1369315139):
        self.base_url = base_url
        self.document_path = document_path
        self.document_url = None
        if document_path is not None:
            self.document_url = "{0}/{1}".format(
                self.base_url, self.document_path)
        self.export_page = export_page
        self.export_format = export_format
        self.logger = utils.get_logger("txpyfind.client.Find")

    def _fetch(self, url):
        return utils.json_request(url)

    def set_data_params(self, url, data_format=None, type_num=None):
        if data_format is None:
            data_format = self.export_format
        if type_num is None:
            type_num = self.export_page
        return utils.append_tx_data_params(url, data_format=data_format,
                                           type_num=type_num, mode="?")

    def add_data_params(self, url, data_format=None, type_num=None):
        if data_format is None:
            data_format = self.export_format
        if type_num is None:
            type_num = self.export_page
        return utils.append_tx_data_params(url, data_format=data_format,
                                           type_num=type_num, mode="&")

    def url_document(self, doc_id, data_format=None, type_num=None):
        if self.document_url is not None:
            doc_url = "{0}/{1}".format(self.document_url, doc_id)
            return self.set_data_params(doc_url, data_format=data_format,
                                        type_num=type_num)

    def get_document(self, document_id, data_format=None,
                     parser_class=parser.JSONResponse):
        url = self.url_document(document_id, data_format=data_format)
        if url is not None:
            doc = self._fetch(url)
            if doc is not None:
                return parser_class(doc)
