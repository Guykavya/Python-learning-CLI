from pathlib import Path


def find_module_file(name, folders):
    for folder in folders:
        base = Path(folder)
        package = base / name / "__init__.py"
        if package.is_file():
            return package
        module = base / f"{name}.py"
        if module.is_file():
            return module
    return None
