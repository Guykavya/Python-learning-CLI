import os
import sqlite3


def backup(src_path, dst_path):
    if os.path.exists(dst_path):
        raise FileExistsError(dst_path)
    source = sqlite3.connect(src_path)
    target = sqlite3.connect(dst_path)
    try:
        source.backup(target)              # the online backup API: a consistent snapshot of committed data
    finally:
        target.close()
        source.close()
