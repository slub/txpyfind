import html
import json
import logging


class JSONResponse:

    def __init__(self, plain):
        self.plain = plain
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        try:
            self.raw = json.loads(plain)
        except json.decoder.JSONDecodeError as err:
            self.logger.error(err)
            self.raw = None
        self.fields = self._names(raw=self.raw)

    def _names(self, raw=None):
        if raw is None:
            raw = self.raw
        if isinstance(raw, dict):
            return list(raw.keys())
        return []

    def _field(self, name, raw=None):
        if raw is None:
            raw = self.raw
        if isinstance(raw, dict) and name in raw:
            return self._unescape(raw[name])

    def _unescape(self, value):
        if isinstance(value, str):
            return html.unescape(value.strip())
        elif isinstance(value, list) and len(value) > 0 and all(isinstance(v, str) and len(v.strip()) > 0 for v in value):
            return [html.unescape(v.strip()) for v in value]
        else:
            return value
