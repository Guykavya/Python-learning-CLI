import os
from pathlib import Path


def rotate_logs(path, keep=3):
    if keep < 1:
        raise ValueError("keep must be at least 1")
    path = Path(path)

    def numbered(i):
        return path.with_name(f"{path.name}.{i}")

    numbered(keep).unlink(missing_ok=True)
    for i in range(keep - 1, 0, -1):
        if numbered(i).exists():
            os.replace(numbered(i), numbered(i + 1))
    if path.exists():
        os.replace(path, numbered(1))


def append_log(path, line, max_bytes=1000, keep=3):
    path = Path(path)
    text = line + "\n"
    size = path.stat().st_size if path.exists() else 0
    if size + len(text.encode("utf-8")) > max_bytes:
        rotate_logs(path, keep)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(text)
