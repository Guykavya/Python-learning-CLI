import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def working_dir(path):
    # TODO: remember the old folder, chdir, yield, and restore in finally
    yield None
