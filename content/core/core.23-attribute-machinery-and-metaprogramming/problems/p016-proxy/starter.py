class ReadOnlyProxy:
    """Read-only view of another object that counts attribute reads.

    Write __init__, __getattr__, __setattr__, __delattr__, access_count and __repr__.
    """

    def __init__(self, target):
        self._target = target
