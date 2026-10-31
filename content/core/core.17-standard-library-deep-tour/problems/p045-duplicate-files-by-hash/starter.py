import hashlib
from collections import defaultdict
from pathlib import Path


def file_hash(path):
    """SHA-256 hex digest, read in chunks."""
    return ""


def find_duplicates(root):
    """Groups (sorted lists of relative posix paths) of 2+ identical non-empty files, sorted."""
    return []


def wasted_bytes(root, groups):
    return 0
