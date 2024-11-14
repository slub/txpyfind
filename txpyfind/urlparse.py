import re
from urllib.parse import unquote_plus as unquote

QUERY = re.compile(r"tx_find_find\[q\]\[([^]]*)\]=([^&]*)")
QUERY_AMP = re.compile(r"=([^&]*%26[^&]*)")
SUBSTITUTE = "%#"
FACET = re.compile(r"tx_find_find\[facet\]\[([^]]*)\]\[([^]]*)\]=1&?")
PAGE = re.compile(r"tx_find_find\[page\]=(\d*)&?")
COUNT = re.compile(r"tx_find_find\[count\]=(\d*)&?")
SORT = re.compile(r"tx_find_find\[sort\]=([a-zA-Z]*)[+ ]([a-zA-Z]*)&?")


class URLParser:

    def __init__(self, url):
        self.url = url
        query_details = get_query(url)
        self.ok = False
        if len(query_details) > 1:
            self.query = query_details[1]
            self.qtype = query_details[0]
            self.ok = True
        self.facets = get_facets(url)
        self.page = get_page(url)
        self.count = get_count(url)
        self.sort = get_sort(url)


def preserve_ampersand(url):
    amps = QUERY_AMP.findall(url)
    if len(amps) == 1:
        url = url.replace(amps[0], amps[0].replace("%", SUBSTITUTE))
        return url, True
    return url, False


def find_query(url):
    url, ampersand = preserve_ampersand(url)
    url = unquote(url)
    if ampersand:
        return [tuple(unquote(e.replace(SUBSTITUTE, "%"))
                      for e in q)
                for q in QUERY.findall(url)]
    return QUERY.findall(url)


def find_facets(url):
    return FACET.findall(unquote(url))


def find_page(url):
    return PAGE.findall(unquote(url))


def find_count(url):
    return COUNT.findall(unquote(url))


def find_sort(url):
    return SORT.findall(unquote(url))


def get_query(url):
    query = find_query(url)
    if len(query) == 1:
        qtype = query[0][0]
        qval = query[0][1]
        qval = re.sub(" +", " ", qval)
        qval = re.sub("^ *| *$", "", qval)
        return qtype, qval
    return ()


def get_facets(url):
    facets = find_facets(url)
    if len(facets) > 0:
        f = []
        for facet in facets:
            f.append({facet[0]: facet[1]})
        return f
    return {}


def get_page(url):
    page = find_page(url)
    if len(page) == 1:
        return int(page[0])
    return 0


def get_count(url):
    count = find_count(url)
    if len(count) > 0:
        return int(count[0])
    return 0


def get_sort(url):
    sort = find_sort(url)
    if len(sort) > 0:
        return "{0} {1}".format(sort[0][0], sort[0][1])
    return ""
