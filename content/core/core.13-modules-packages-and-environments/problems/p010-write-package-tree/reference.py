from pathlib import Path, PurePosixPath


def write_package(root, files):
    all_files = dict(files)
    for rel in files:
        for folder in PurePosixPath(rel).parents:
            if str(folder) == ".":
                continue
            all_files.setdefault(f"{folder}/__init__.py", "")
    for rel, text in all_files.items():
        target = Path(root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return sorted(all_files)
