class Config:
    """Read-only, dotted-access view of a nested dict.

    Write __getattr__, __dir__ and to_dict.
    """

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data[name]
