import json
import inspect
import logging
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from ._version import __version__


def get_request(url):
    logger = logging.getLogger(f"{__name__}.{inspect.currentframe().f_code.co_name}")
    req = Request(url)
    req.add_header("User-Agent", f"txpyfind {__version__}")
    try:
        with urlopen(req) as response:
            if response.code == 200:
                return response.read()
            else:
                logger.error("HTTP %d GET %s", response.code, url)
    except Exception as e:
        logger.error(e)


def plain_request(url):
    payload = get_request(url)
    if isinstance(payload, bytes):
        try:
            return payload.decode()
        except Exception as e:
            logger = logging.getLogger(f"{__name__}.{inspect.currentframe().f_code.co_name}")
            logger.error(e)


def json_request(url):
    plain = plain_request(url)
    if isinstance(plain, str):
        try:
            return json.loads(plain)
        except json.decoder.JSONDecodeError:
            logger = logging.getLogger(f"{__name__}.{inspect.currentframe().f_code.co_name}")
            logger.error("Got faulty JSON from URL %s", url)


def url_encode(urlstr):
    return quote_plus(urlstr)


def json_str(jsondict):
    return json.dumps(jsondict)


def json_str_pretty(jsondict, indent=2):
    return json.dumps(jsondict, indent=indent)


def add_param(url, key, value=None):
    url = f"{url}&{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def set_param(url, key, value=None):
    url = f"{url}?{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def tx_param(key, index=None):
    if isinstance(key, str):
        k = f"[{key}]"
    else:
        k = "".join(f"[{k}]" for k in key)
    if isinstance(index, int):
        k += f"[{index}]"
    return f"tx_find_find{k}"


def add_tx_param(url, key, value, index=None):
    return add_param(url, tx_param(key,  index=index), value)


def set_tx_param(url, key, value, index=None):
    return set_param(url, tx_param(key, index=index), value)


def tx_param_data(data_format, type_num=1369315139):
    param = f"{tx_param('format')}=data"
    param = add_tx_param(param, "data-format", data_format)
    return add_param(param, "type", type_num)


def add_tx_param_data(url, data_format, type_num=1369315139):
    return add_param(url, tx_param_data(data_format, type_num=type_num))


def set_tx_param_data(url, data_format, type_num=1369315139):
    return set_param(url, tx_param_data(data_format, type_num=type_num))
