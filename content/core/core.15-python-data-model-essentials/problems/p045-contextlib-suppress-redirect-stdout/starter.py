import io
import os
from contextlib import redirect_stderr, redirect_stdout, suppress


def capture(func, *args, **kwargs):
    return None, "", ""


def remove_if_exists(path):
    return False


def to_int_or(text, default=None):
    return default
