import weakref

_instances = weakref.WeakSet()


def _release(name, log):
    """The cleanup callback: it gets only the name and the log, never the resource itself."""
    log.append(f"close {name}")


class TempResource:
    """A resource that is closed exactly once: explicitly, by `with`, or when collected."""

    def __init__(self, name, log):
        self.name = name
        log.append(f"open {name}")
        self._finalizer = weakref.finalize(self, _release, name, log)
        _instances.add(self)

    def close(self):
        self._finalizer()            # runs _release the first time, does nothing afterwards

    @property
    def closed(self):
        return not self._finalizer.alive

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def live_resources():
    """Sorted names of TempResource objects that still exist and are not closed."""
    return sorted(r.name for r in list(_instances) if not r.closed)
