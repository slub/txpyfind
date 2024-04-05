import re
from . import utils
from . import parser


class Find:

    def __init__(self,
                 base_url,
                 document_path=None,
                 query_types=["default"],
                 facets=[],
                 count_limit=100,
                 sort_pattern=None,
                 export_format="raw-solr-response",
                 export_page=1369315139):
        self.base_url = base_url
        self.document_path = document_path
        self.query_types = query_types
        self.facets = facets
        self.count_limit = count_limit
        self.sort_pattern = sort_pattern
        self.document_url = None
        if document_path is not None:
            self.document_url = "{0}/{1}".format(
                self.base_url, self.document_path)
        self.export_page = export_page
        self.export_format = export_format
        self.logger = utils.get_logger("txpyfind.client.Find")

    def set_data_params(self, url, data_format=None, type_num=None):
        if data_format is None:
            data_format = self.export_format
        if type_num is None:
            type_num = self.export_page
        return utils.set_tx_param_data(url, data_format=data_format, type_num=type_num)

    def add_data_params(self, url, data_format=None, type_num=None):
        if data_format is None:
            data_format = self.export_format
        if type_num is None:
            type_num = self.export_page
        return utils.add_tx_param_data(url, data_format=data_format, type_num=type_num)

    def url_document(self, doc_id, data_format=None, type_num=None):
        if self.document_url is not None:
            doc_url = "{0}/{1}".format(self.document_url, doc_id)
            return self.set_data_params(doc_url, data_format=data_format, type_num=type_num)

    def get_document(self, document_id, data_format=None, type_num=None, parser_class=parser.JSONResponse):
        url = self.url_document(document_id, data_format=data_format, type_num=type_num)
        if url is not None:
            doc = utils.json_request(url)
            if doc is not None:
                if parser_class is not None:
                    return parser_class(doc)
                return doc

    def url_query(self, query, qtype="default", facet={}, page=0, count=0, sort="", data_format=None, type_num=None):
        if qtype not in self.query_types:
            self.logger.warning("Unknown query type!")
            qtype = "default"
        url = utils.set_tx_param(self.base_url, ["q", qtype], utils.url_encode(query))
        url = self.add_data_params(url, data_format=data_format, type_num=type_num)
        for f in facet:
            if type(f) == str:
                if f not in self.facets:
                    self.logger.warning(f"Unknown facet type {f}!")
                    continue
                url = utils.add_tx_param(url, ["facet", f, utils.url_encode(facet[f])], 1)
            elif type(f) == dict:
                for k in f:
                    if k not in self.facets:
                        self.logger.warning(f"Unknown facet type {k}!")
                        continue
                    url = utils.add_tx_param(url, ["facet", k, utils.url_encode(f[k])], 1)
        if page:
            url = utils.add_tx_param(url, "page", page)
        if count:
            if count > self.count_limit:
                self.logger.warning(f"Count {count} exceeds limit!")
                count = self.count_limit
            url = utils.add_tx_param(url, "count", count)
        if sort != "" and self.sort_pattern is not None and not isinstance(self.sort_pattern.match(sort), re.Match):
            self.logger.warning(f"Sort instruction {sort} is unknown!")
            sort = ""
        if sort != "":
            url = utils.add_tx_param(url, "sort", utils.url_encode(sort))
        return url

    def get_query(self, query, qtype="default", facet={}, page=0, count=0, sort="", data_format=None, type_num=None):
        url = self.url_query(query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format=data_format, type_num=type_num)
        return utils.json_request(url)
