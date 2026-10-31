import importlib.util
import tempfile
from pathlib import Path

import coverage


def measure(source, func_name, calls):
    with tempfile.TemporaryDirectory() as tmp:
        path = (Path(tmp) / "target_mod.py").resolve()
        path.write_text(source)
        cov = coverage.Coverage(data_file=None, include=[str(path)])
        cov.start()
        try:
            spec = importlib.util.spec_from_file_location("target_mod_under_test", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            func = getattr(module, func_name)
            for args in calls:
                try:
                    func(*args)
                except Exception:
                    pass
        finally:
            cov.stop()
        _, statements, _, missing, _ = cov.analysis2(str(path))
    done = len(statements) - len(missing)
    return round(100 * done / len(statements), 1), sorted(missing)
