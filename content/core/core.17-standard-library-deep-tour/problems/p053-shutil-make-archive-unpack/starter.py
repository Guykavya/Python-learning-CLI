import shutil
import tarfile
import zipfile
from pathlib import Path


def archive_formats():
    return []


def make_backup(src_dir, out_dir, name, fmt="zip"):
    return Path()


def archive_members(archive):
    return []


def restore(archive, dest):
    return []
