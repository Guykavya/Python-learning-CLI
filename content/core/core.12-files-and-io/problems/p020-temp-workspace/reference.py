import tempfile
from pathlib import Path


def sort_via_temp(text):
    lines = text.splitlines()
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "work.txt"
        with open(path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        with open(path, encoding="utf-8") as f:
            back = [line.rstrip("\n") for line in f]
        return sorted(back), str(path)
