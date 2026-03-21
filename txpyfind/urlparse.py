"""Extract TYPO3-find query parameters from URLs."""
import re
from urllib.parse import unquote_plus as unquote

QUERY = re.compile(r"tx_find_find\[q\]\[([^]]*)\]=([^&]*)")
QUERY_AMP = re.compile(r"=([^&]*%26[^&]*)")
SUBSTITUTE = "%#"
FACET = re.compile(r"tx_find_find\[facet\]\[([^]]*)\]\[([^]]*)\]=1&?")
PAGE = re.compile(r"tx_find_find\[page\]=(\d*)&?")
COUNT = re.compile(r"tx_find_find\[count\]=(\d*)&?")
SORT = re.compile(r"tx_find_find\[sort\]=([a-zA-Z0-9_]*)[+ ]([a-zA-Z0-9_]*)&?")


class URLParser:  # pylint: disable=R0902,R0903
    """Parse TYPO3-find query parameters from a URL."""

    def __init__(self, url):
        """Parse TYPO3-find parameters from the given URL."""
        self.url = url
        self.query = ""
        self.qtype = ""
        query_details = get_query(url)
        self.is_ok = False
        if len(query_details) > 1:
            self.query = query_details[1]
            self.qtype = query_details[0]
            self.is_ok = True
        self.facets = get_facets(url)
        self.page = get_page(url)
        self.count = get_count(url)
        self.sort = get_sort(url)


def preserve_ampersand(url):
    """Preserve ampersand in the given URL."""
    amps = QUERY_AMP.findall(url)
    if len(amps) == 1:
        url = url.replace(amps[0], amps[0].replace("%", SUBSTITUTE))
        return url, True
    return url, False


def find_query(url):
    """Find query parameter in the given URL."""
    url, ampersand = preserve_ampersand(url)
    url = unquote(url)
    if ampersand:
        return [tuple(unquote(e.replace(SUBSTITUTE, "%"))
                      for e in q)
                for q in QUERY.findall(url)]
    return QUERY.findall(url)


def find_facets(url):
    """Find facet parameters in the given URL."""
    return FACET.findall(unquote(url))


def find_page(url):
    """Find page parameter in the given URL."""
    return PAGE.findall(unquote(url))


def find_count(url):
    """Find count parameter in the given URL."""
    return COUNT.findall(unquote(url))


def find_sort(url):
    """Find sort parameter in the given URL."""
    return SORT.findall(unquote(url))


def get_query(url):
    """Get query parameter from the given URL."""
    query = find_query(url)
    if len(query) == 1:
        qtype = query[0][0]
        qval = query[0][1]
        qval = re.sub(" +", " ", qval)
        qval = re.sub("^ *| *$", "", qval)
        return qtype, qval
    return ()


def get_facets(url):
    """Get facet parameters from the given URL."""
    facets = find_facets(url)
    if len(facets) > 0:
        fct = []
        for facet in facets:
            fct.append({facet[0]: facet[1]})
        return fct
    return []


def get_page(url):
    """Get page parameter from the given URL."""
    page = find_page(url)
    if len(page) == 1:
        return int(page[0])
    return 0


def get_count(url):
    """Get count parameter from the given URL."""
    count = find_count(url)
    if len(count) > 0:
        return int(count[0])
    return 0


def get_sort(url):
    """Get sort parameter from the given URL."""
    sort = find_sort(url)
    if len(sort) > 0:
        return f"{sort[0][0]} {sort[0][1]}"
    return ""
