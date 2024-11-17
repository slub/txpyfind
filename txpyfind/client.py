import re
from . import utils
from . import parser
from . import urlparse


class Find:

    def __init__(self,
                 base_url,
                 document_path=None,
                 query_types=["default"],
                 facets=[],
                 count_limit=100,
                 sort_pattern=None,
                 export_format="raw-solr-response",
                 export_page=1369315139,
                 parser_class=parser.JSONResponse):
        self.base_url = base_url
        self.document_path = document_path
        self.query_types = query_types
        self.facets = facets
        self.count_limit = count_limit
        self.sort_pattern = sort_pattern
        self.document_url = None
        if document_path is not None:
            self.document_url = f"{self.base_url}/{self.document_path}"
        self.export_page = export_page
        self.export_format = export_format
        self.parser_class = parser_class
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

    def add_facet_params(self, url, facet={}):
        for f in facet:
            if isinstance(f, str):
                if f not in self.facets:
                    self.logger.warning("Unknown facet type %s!", f)
                    continue
                url = utils.add_tx_param(url, ["facet", f, utils.url_encode(facet[f])], 1)
            elif isinstance(f, dict):
                for k in f:
                    if k not in self.facets:
                        self.logger.warning("Unknown facet type %s!", k)
                        continue
                    url = utils.add_tx_param(url, ["facet", k, utils.url_encode(f[k])], 1)
        return url

    def url_document(self, doc_id, data_format=None, type_num=None):
        if self.document_url is not None:
            doc_url = f"{self.document_url}/{doc_id}"
            return self.set_data_params(doc_url, data_format=data_format, type_num=type_num)

    def get_document(self, document_id, data_format=None, type_num=None, parser_class=None):
        url = self.url_document(document_id, data_format=data_format, type_num=type_num)
        if url is not None:
            doc = utils.plain_request(url)
            if doc is not None:
                if parser_class is not None:
                    return parser_class(doc)
                if self.parser_class is not None:
                    return self.parser_class(doc)
                return doc

    def url_query(self, query, qtype="default", facet={}, page=0, count=0, sort="", data_format=None, type_num=None):
        if qtype not in self.query_types:
            self.logger.warning("Unknown query type!")
            qtype = "default"
        url = utils.set_tx_param(self.base_url, ["q", qtype], utils.url_encode(query))
        url = self.add_data_params(url, data_format=data_format, type_num=type_num)
        url = self.add_facet_params(url, facet=facet)
        if page:
            url = utils.add_tx_param(url, "page", page)
        if count:
            if count > self.count_limit:
                self.logger.warning("Count %d exceeds limit!", count)
                count = self.count_limit
            url = utils.add_tx_param(url, "count", count)
        if sort != "" and self.sort_pattern is not None and not isinstance(self.sort_pattern.match(sort), re.Match):
            self.logger.warning("Sort instruction %s is unknown!", sort)
            sort = ""
        if sort != "":
            url = utils.add_tx_param(url, "sort", utils.url_encode(sort))
        return url

    def get_query(self, query, qtype="default", facet={}, page=0, count=0, sort="",
                  data_format=None, type_num=None, parser_class=None):
        url = self.url_query(query, qtype=qtype, facet=facet, page=page, count=count, sort=sort,
                             data_format=data_format, type_num=type_num)
        response = utils.plain_request(url)
        if response is not None:
            if parser_class is not None:
                return parser_class(response)
            if self.parser_class is not None:
                return self.parser_class(response)
            return response

    def get_query_via_url(self, url, data_format=None, type_num=None, parser_class=None):
        url = urlparse.URLParser(url)
        if url.ok:
            return self.get_query(url.query, qtype=url.qtype, facet=url.facets, page=url.page, count=url.count, sort=url.sort,
                                  data_format=data_format, type_num=type_num, parser_class=parser_class)

    def scroll_get_query(self, query, qtype="default", facet={}, batch=20, sort="", data_format="raw-solr-response",
                         type_num=None, parser_class=None):
        if data_format is None:
            data_format = self.export_format
        if data_format != "raw-solr-response":
            self.logger.warning("Scrolling only supports data format of type 'raw-solr-response'!")
            data_format = "raw-solr-response"
        response = self.get_query(query, qtype=qtype, facet=facet, sort=sort, data_format=data_format,
                                  type_num=type_num, parser_class=parser_class)
        if hasattr(response, "raw") and isinstance(response.raw, dict) and "response" in response.raw:
            data = response.raw["response"]
            total = data["numFound"]
            docs = []
            pages = int(total / batch) + (total % batch > 0)
            for i in range(1, pages+1):
                response_i = self.get_query(query, qtype=qtype, facet=facet, page=i, count=batch, sort=sort,
                                            data_format=data_format, type_num=type_num, parser_class=parser_class)
                if hasattr(response_i, "raw") and isinstance(response_i.raw, dict) and "response" in response_i.raw:
                    data_i = response_i.raw["response"]
                    if "docs" in data_i:
                        for doc in data_i["docs"]:
                            docs.append(doc)
            if total != len(docs):
                self.logger.warning("Expected %d record%s for query %s. Got %d record%s.",
                                    total, 's' if total != 1 else '', query, len(docs), 's' if len(docs) != 1 else '')
            return docs

    def stream_get_query(self, query, qtype="default", facet={}, batch=20, sort="", data_format="raw-solr-response",
                         type_num=None, parser_class=None):
        if data_format is None:
            data_format = self.export_format
        if data_format != "raw-solr-response":
            self.logger.warning("Streaming only supports data format of type 'raw-solr-response'!")
            data_format = "raw-solr-response"
        response = self.get_query(query, qtype=qtype, facet=facet, sort=sort, data_format=data_format,
                                  type_num=type_num, parser_class=parser_class)
        if not hasattr(response, "raw") or not isinstance(response.raw, dict) or "response" not in response.raw:
            return None
        data = response.raw["response"]
        total = data["numFound"]
        pages = int(total / batch) + (total % batch > 0)
        for i in range(1, pages+1):
            response_i = self.get_query(query, qtype=qtype, facet=facet, page=i, count=batch, sort=sort,
                                        data_format=data_format)
            if hasattr(response_i, "raw") and isinstance(response_i.raw, dict) and "response" in response_i.raw:
                data_i = response_i.raw["response"]
                if "docs" in data_i:
                    for doc in data_i["docs"]:
                        yield doc
