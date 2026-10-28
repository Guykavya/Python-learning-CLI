import os
from pathlib import Path


def rotate_logs(path, keep=3):
    # TODO: delete the oldest, shift .i to .i+1 from the oldest down, then path -> path.1
    pass


def append_log(path, line, max_bytes=1000, keep=3):
    # TODO: rotate first if the file would get too big, then append line + newline
    pass
