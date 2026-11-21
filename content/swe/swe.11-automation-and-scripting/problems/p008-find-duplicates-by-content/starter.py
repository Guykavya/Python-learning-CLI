import hashlib
from pathlib import Path


def sha256_of(path, chunk=1024 * 1024):
    """Hex SHA-256 of a file, read in chunks."""
    # TODO
    return ""


def find_duplicates(root, min_size=1):
    """Groups of files with identical content. Cheap check (size) first, expensive hash second."""
    # TODO
    return []
