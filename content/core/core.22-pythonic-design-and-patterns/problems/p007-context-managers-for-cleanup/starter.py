def read_all(open_resource, name):
    """Open the resource, return everything read from it, always close it."""
    r = open_resource(name)
    try:
        return r.read()
    finally:
        r.close()


def copy_text(open_resource, src, dst):
    """Write everything read from src into dst. Return the number of characters copied.
    Both resources must be closed, whatever happens."""
    s = open_resource(src)
    try:
        d = open_resource(dst)
        try:
            text = s.read()
            d.write(text)
            return len(text)
        finally:
            d.close()
    finally:
        s.close()


def run_locked(lock, func):
    """Call func() while holding the lock. Return its result."""
    lock.acquire()
    try:
        return func()
    finally:
        lock.release()


def temp_setting(obj, name, value):
    """Meant to be used as: with temp_setting(cfg, 'precision', 2): ...
    (Not written yet: the callers below do it by hand.)"""
    raise NotImplementedError


def format_with_precision(cfg, numbers, precision):
    """[cfg.fmt(n) for n in numbers] with cfg.precision temporarily set to precision."""
    old = cfg.precision
    cfg.precision = precision
    try:
        return [cfg.fmt(n) for n in numbers]
    finally:
        cfg.precision = old
