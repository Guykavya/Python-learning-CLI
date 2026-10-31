import importlib
import sys
from pathlib import Path


def create_module(folder, name, source):
    path = Path(folder)
    (path / f"{name}.py").write_text(source, encoding="utf-8")
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    importlib.invalidate_caches()
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)
