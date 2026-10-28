import os
from pathlib import Path, PurePosixPath


def disk_usage(root, skip=()):
    """Folder (relative, posix, '.' for root) -> total bytes including sub-folders."""
    return {}


def largest_files(root, n, skip=()):
    """The n biggest files as (relative_path, size): biggest first, ties by path."""
    return []


def human_size(nbytes):
    """'512 B', '1.5 KiB', '2.0 MiB', ... up to TiB."""
    return ""
