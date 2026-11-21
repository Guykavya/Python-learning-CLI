import os
import re
import shutil
from pathlib import Path

VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def current_version(root):
    pointer = Path(root) / "current"
    return pointer.read_text(encoding="utf-8").strip() if pointer.exists() else None


def deploy(root, version, files, health_check, keep=5):
    # TODO: validate, write the release atomically, switch the pointer, health check, roll back, prune
    return {"version": version, "status": "failed", "live": None, "error": "not implemented"}
