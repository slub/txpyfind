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
    send HTTP GET request to given URL
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
    request data in plain text format from given URL
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
    request data in JSON format from given URL
    """
    plain = plain_request(url)
    if isinstance(plain, str):
        try:
            return json.loads(plain)
        except json.decoder.JSONDecodeError:
            logger.error("Got faulty JSON from URL %s", url)
    return None


def url_encode(url):
    """
    encode given URL
    """
    return quote_plus(url)


def set_param(url, key, value=None):
    """
    add initial parameter to given URL
    """
    url = f"{url}?{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def add_param(url, key, value=None):
    """
    add subsequent parameter to given URL
    """
    url = f"{url}&{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def tx_param(key, index=None):
    """
    create URL parameter for TYPO3-find
    """
    if isinstance(key, str):
        k = f"[{key}]"
    else:
        k = "".join(f"[{k}]" for k in key)
    if isinstance(index, int):
        k += f"[{index}]"
    return f"tx_find_find{k}"


def set_tx_param(url, key, value, index=None):
    """
    add TYPO3-find parameter as initial parameter to given URL
    """
    return set_param(url, tx_param(key, index=index), value)


def add_tx_param(url, key, value, index=None):
    """
    add TYPO3-find parameter as subsequent parameter to given URL
    """
    return add_param(url, tx_param(key,  index=index), value)


def tx_param_data(data_format, type_num=1369315139):
    """
    create parameters for TYPO3-find data exports
    """
    param = f"{tx_param('format')}=data"
    param = add_tx_param(param, "data-format", data_format)
    return add_param(param, "type", type_num)


def set_tx_param_data(url, data_format, type_num=1369315139):
    """
    add parameters for TYPO3-find data exports as initial parameters to given URL
    """
    return set_param(url, tx_param_data(data_format, type_num=type_num))


def add_tx_param_data(url, data_format, type_num=1369315139):
    """
    add parameters for TYPO3-find data exports as subsequent parameters to given URL
    """
    return add_param(url, tx_param_data(data_format, type_num=type_num))
