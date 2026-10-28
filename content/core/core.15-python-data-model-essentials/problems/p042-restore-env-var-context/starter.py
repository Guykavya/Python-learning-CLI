import os
from contextlib import contextmanager


@contextmanager
def temp_env(**changes):
    # TODO: set the variables, yield, then restore the old state
    yield os.environ
