def _plain(value):
    """Deep copy of nested dicts and lists."""
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


class Config:
    """Read-only, dotted-access view of a nested dict."""

    def __init__(self, data, path=""):
        self._data = data
        self._path = path

    def __getattr__(self, name):
        # vars(self) never calls __getattr__, so a half-built Config cannot recurse.
        data = vars(self).get("_data", {})
        full = f"{vars(self).get('_path', '')}.{name}".lstrip(".")
        try:
            value = data[name]
        except KeyError:
            raise AttributeError(f"no config key {full!r}") from None
        if isinstance(value, dict):
            return Config(value, full)
        return value

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(self._data))

    def to_dict(self):
        return _plain(self._data)
