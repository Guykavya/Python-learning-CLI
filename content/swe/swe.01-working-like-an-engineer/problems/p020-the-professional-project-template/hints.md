## Hint 1

Which files does a project need? Make a dictionary from the relative path to the text of the file, with `{name}` placeholders. How do you fill the placeholders (`str.format` or `replace`) and avoid problems with curly braces in the files (a TOML table never uses `{}` here, but a Python f-string in `tasks.py` does)?

## Hint 2

Put the text of `tasks.py` in a normal (non-formatted) string, and use `.replace("{name}", name)` only on the files that need it, or write `{{` and `}}` where `.format` is used. Create parent folders with `path.parent.mkdir(parents=True, exist_ok=True)`. Write bytes: `path.write_bytes(text.encode("utf-8"))`.

## Hint 3

```text
validate name with re.fullmatch(r"[a-z][a-z0-9_]*", name)  -> ValueError
project = Path(root) / name; if project.exists(): raise FileExistsError
files = { "pyproject.toml": ..., "README.md": ..., "CHANGELOG.md": ..., ".gitignore": ..., "LICENSE": ...,
          "tasks.py": ..., f"src/{name}/__init__.py": ..., f"src/{name}/py.typed": "", f"tests/test_{name}.py": ... }
write them all, return project
```
