import json
import logging
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from . import __version__


def get_logger(name, loglevel=logging.WARNING):
    logger = logging.getLogger(name)
    if not logger.handlers:
        stream = logging.StreamHandler()
        stream.setLevel(loglevel)
        stream.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(stream)
    if logger.level != loglevel:
        logger.setLevel(loglevel)
    return logger


def get_request(url):
    logger = get_logger("txpyfind.utils.get_request")
    req = Request(url)
    req.add_header("User-Agent", "txpyfind {0}".format(__version__))
    try:
        with urlopen(req) as response:
            if response.code == 200:
                return response.read()
            else:
                logger.error("HTTP request to {0} failed!".format(url))
                logger.error("HTTP response code is {0}.".format(response.code))
    except Exception as e:
        logger.error(e)


def plain_request(url):
    logger = get_logger("txpyfind.utils.plain_request")
    payload = get_request(url)
    try:
        return payload.decode()
    except Exception as e:
        logger.error(e)


def json_request(url):
    logger = get_logger("txpyfind.utils.json_request")
    plain = plain_request(url)
    try:
        return json.loads(plain)
    except json.decoder.JSONDecodeError:
        logger.error("Parsing JSON data retrieved from {0} failed!".format(url))


def url_encode(urlstr):
    return quote_plus(urlstr)


def json_str(jsondict):
    return json.dumps(jsondict)


def json_str_pretty(jsondict, indent=2):
    return json.dumps(jsondict, indent=indent)


def add_param(url, key, value=None):
    url = "{0}&{1}".format(url, key)
    if value is not None:
        url = "{0}={1}".format(url, value)
    return url


def set_param(url, key, value=None):
    url = "{0}?{1}".format(url, key)
    if value is not None:
        url = "{0}={1}".format(url, value)
    return url


def tx_param(key):
    """
    [0]
    """
    if isinstance(key, str):
        k = "[{}]".format(key)
    else:
        k = "".join("[{0}]".format(k) for k in key)
    # k += "[0]"
    return "tx_find_find{0}".format(k)


def add_tx_param(url, key, value):
    return add_param(url, tx_param(key), value)


def set_tx_param(url, key, value):
    return set_param(url, tx_param(key), value)


def tx_param_data(data_format, type_num=1369315139):
    param = "{0}={1}".format(tx_param("format"), "data")
    param = add_tx_param(param, "data-format", data_format)
    return add_param(param, "type", type_num)


def append_tx_data_params(url, mode, data_format=None, type_num=None):
    if mode not in ["?", "&"]:
        raise Exception
    data_param = tx_param_data(data_format, type_num=type_num)
    return "{0}{1}{2}".format(url, mode, data_param)
