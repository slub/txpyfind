"""
utils module of ``txpyfind`` package
"""
import json
import logging
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from ._version import __version__


logger = logging.getLogger(__name__)


def get_request(url):
    """
    get_request
    """
    req = Request(url)
    req.add_header("User-Agent", f"txpyfind {__version__}")
    try:
        with urlopen(req) as response:
            if response.code == 200:
                return response.read()
            logger.error("HTTP %d GET %s", response.code, url)
    except Exception as exc:
        logger.error(exc)
    return None


def plain_request(url):
    """
    plain_request
    """
    payload = get_request(url)
    if isinstance(payload, bytes):
        try:
            return payload.decode()
        except Exception as exc:
            logger.error(exc)
    return None


def json_request(url):
    """
    json_request
    """
    plain = plain_request(url)
    if isinstance(plain, str):
        try:
            return json.loads(plain)
        except json.decoder.JSONDecodeError:
            logger.error("Got faulty JSON from URL %s", url)
    return None


def url_encode(urlstr):
    """
    url_encode
    """
    return quote_plus(urlstr)


def json_str(jsondict):
    """
    json_str
    """
    return json.dumps(jsondict)


def json_str_pretty(jsondict, indent = 2):
    """
    json_str_pretty
    """
    return json.dumps(jsondict, indent=indent)


def add_param(url, key, value = None):
    """
    add_param
    """
    url = f"{url}&{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def set_param(url, key, value = None):
    """
    set_param
    """
    url = f"{url}?{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def tx_param(key, index = None):
    """
    tx_param
    """
    if isinstance(key, str):
        k = f"[{key}]"
    else:
        k = "".join(f"[{k}]" for k in key)
    if isinstance(index, int):
        k += f"[{index}]"
    return f"tx_find_find{k}"


def add_tx_param(url, key, value, index = None):
    """
    add_tx_param
    """
    return add_param(url, tx_param(key,  index=index), value)


def set_tx_param(url, key, value, index = None):
    """
    set_tx_param
    """
    return set_param(url, tx_param(key, index=index), value)


def tx_param_data(data_format, type_num = 1369315139):
    """
    tx_param_data
    """
    param = f"{tx_param('format')}=data"
    param = add_tx_param(param, "data-format", data_format)
    return add_param(param, "type", type_num)


def add_tx_param_data(url, data_format, type_num = 1369315139):
    """
    add_tx_param_data
    """
    return add_param(url, tx_param_data(data_format, type_num=type_num))


def set_tx_param_data(url, data_format, type_num = 1369315139):
    """
    set_tx_param_data
    """
    return set_param(url, tx_param_data(data_format, type_num=type_num))
