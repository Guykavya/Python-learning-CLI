from pathlib import Path


def list_by_suffix(folder, suffix):
    names = []
    for item in Path(folder).iterdir():
        if item.is_file() and item.suffix.lower() == suffix.lower():
            names.append(item.name)
    return sorted(names)
