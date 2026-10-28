import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def atomic_open(path, mode="w", **kwargs):
    # TODO: temp file in the same folder, yield it, os.replace on success, delete on error
    yield None
