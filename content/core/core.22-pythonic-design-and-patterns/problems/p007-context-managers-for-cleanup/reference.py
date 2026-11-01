from contextlib import contextmanager


def read_all(open_resource, name):
    with open_resource(name) as r:
        return r.read()


def copy_text(open_resource, src, dst):
    with open_resource(src) as s, open_resource(dst) as d:
        text = s.read()
        d.write(text)
        return len(text)


def run_locked(lock, func):
    with lock:
        return func()


@contextmanager
def temp_setting(obj, name, value):
    missing = object()
    old = getattr(obj, name, missing)
    setattr(obj, name, value)
    try:
        yield
    finally:
        if old is missing:
            delattr(obj, name)
        else:
            setattr(obj, name, old)


def format_with_precision(cfg, numbers, precision):
    with temp_setting(cfg, "precision", precision):
        return [cfg.fmt(n) for n in numbers]
