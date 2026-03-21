"""URL construction and HTTP utilities for TYPO3-find."""
import json
import logging
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from ._version import __version__


logger = logging.getLogger(__name__)


def get_request(url):
    """Send HTTP GET request to the given URL."""
    req = Request(url)
    req.add_header("User-Agent", f"txpyfind {__version__}")
    try:
        with urlopen(req, timeout=30) as response:
            if response.status == 200:
                return response.read()
            logger.error("HTTP %d GET %s", response.status, url)
    except URLError as exc:
        logger.error("Failed to fetch %s: %s", url, exc)
    return None


def plain_request(url):
    """Request data in plain text format from the given URL."""
    payload = get_request(url)
    if isinstance(payload, bytes):
        try:
            return payload.decode()
        except UnicodeDecodeError as exc:
            logger.error("Failed to decode response from %s: %s", url, exc)
    return None


def json_request(url):
    """Request data in JSON format from the given URL."""
    plain = plain_request(url)
    if isinstance(plain, str):
        try:
            return json.loads(plain)
        except json.decoder.JSONDecodeError:
            logger.error("Got faulty JSON from URL %s", url)
    return None


def url_encode(url):
    """URL-encode the given string."""
    return quote_plus(url)


def set_param(url, key, value=None):
    """Add initial parameter to the given URL."""
    url = f"{url}?{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def add_param(url, key, value=None):
    """Add subsequent parameter to the given URL."""
    url = f"{url}&{key}"
    if value is not None:
        url = f"{url}={value}"
    return url


def tx_param(key, index=None):
    """Create a TYPO3-find URL parameter name."""
    if isinstance(key, str):
        k = f"[{key}]"
    else:
        k = "".join(f"[{k}]" for k in key)
    if isinstance(index, int):
        k += f"[{index}]"
    return f"tx_find_find{k}"


def set_tx_param(url, key, value, index=None):
    """Add a TYPO3-find parameter as initial parameter to the given URL."""
    return set_param(url, tx_param(key, index=index), value)


def add_tx_param(url, key, value, index=None):
    """Add a TYPO3-find parameter as subsequent parameter to the given URL."""
    return add_param(url, tx_param(key,  index=index), value)


def tx_param_data(data_format, type_num=1369315139):
    """Create parameters for TYPO3-find data exports."""
    param = f"{tx_param('format')}=data"
    param = add_tx_param(param, "data-format", data_format)
    return add_param(param, "type", type_num)


def set_tx_param_data(url, data_format, type_num=1369315139):
    """Add TYPO3-find data export parameters as initial parameters to the given URL."""
    return set_param(url, tx_param_data(data_format, type_num=type_num))


def add_tx_param_data(url, data_format, type_num=1369315139):
    """Add TYPO3-find data export parameters as subsequent parameters to the given URL."""
    return add_param(url, tx_param_data(data_format, type_num=type_num))
