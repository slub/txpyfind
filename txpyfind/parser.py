import html


class JSONResponse:

    def __init__(self, raw):
        self.raw = raw
        self.fields = self._names(raw=raw)

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
        elif isinstance(value, list) and len(value) > 0 and all(type(v) == str and len(v.strip()) > 0 for v in value):
            return [html.unescape(v.strip()) for v in value]
        else:
            return value
