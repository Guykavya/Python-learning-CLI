import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def working_dir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield Path.cwd()
    finally:
        os.chdir(old)
