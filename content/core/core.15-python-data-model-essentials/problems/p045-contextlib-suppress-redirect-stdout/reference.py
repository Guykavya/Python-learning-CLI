import io
import os
from contextlib import redirect_stderr, redirect_stdout, suppress


def capture(func, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        result = func(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


def remove_if_exists(path):
    with suppress(FileNotFoundError):
        os.remove(path)
        return True
    return False


def to_int_or(text, default=None):
    with suppress(ValueError, TypeError):
        return int(text)
    return default
