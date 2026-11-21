import hashlib
import sqlite3
import tempfile
import time
from contextlib import closing
from pathlib import Path


def backup(db_file, backup_dir, keep=7, now=time.time):
    # TODO: online backup, integrity check, checksum file, rotation
    raise NotImplementedError


def drill(backup_file, min_orders=1):
    # TODO: checksum, restore into a temporary folder, integrity, table, row count
    raise NotImplementedError
