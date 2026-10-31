from pathlib import Path

# Fill this dict: relative path -> the text of the file.
# Use triple-quoted strings for the file contents.
FILES = {
    # "textkit/__init__.py": """...""",
}


def split_script(root):
    """Write every file in FILES under root. Return the sorted relative paths."""
    root = Path(root)
    for rel, text in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return sorted(FILES)
