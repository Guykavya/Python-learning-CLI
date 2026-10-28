import io
from contextlib import redirect_stderr, redirect_stdout


def capture_output(func, *args, **kwargs):
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        result = func(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()
