import weakref


class TempResource:
    """A resource that is closed exactly once: explicitly, by `with`, or when collected."""

    def __init__(self, name, log):
        self.name = name
        self.log = log
        log.append(f"open {name}")
        self._closed = False
        # TODO: register a weakref.finalize that appends f"close {name}" to log.
        # Careful: the callback and its arguments must not refer to self.

    def close(self):
        # TODO: close exactly once (calling the finalizer does that for you)
        self._closed = True

    @property
    def closed(self):
        return self._closed

    # TODO: __enter__ and __exit__


def live_resources():
    """Sorted names of TempResource objects that still exist and are not closed."""
    # TODO: track instances in a module-level weakref.WeakSet
    return []
