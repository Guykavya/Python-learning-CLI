import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def atomic_open(path, mode="w", **kwargs):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, mode, **kwargs) as f:
            yield f
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
