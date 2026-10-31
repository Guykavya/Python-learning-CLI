## Approach

Coverage watches Python files as they execute, so the source must live in a real file. Write it to a temporary folder, start the
measurement, import the file (this runs the `def` and any module-level lines), call the function once per argument tuple, stop, and ask for the analysis.
`data_file=None` keeps the results in memory so no `.coverage` file is written; the `TemporaryDirectory` removes the source file. `include=[path]` limits
the report to that one file (otherwise coverage would also count the standard library and your own code).

## Code

```python
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
```

## Cost

Dominated by starting and stopping the tracer and importing one tiny file: a few milliseconds per call. Tracing slows the measured code a few times,
which is why you measure in tests, not in production.

## Another way

`cov.report(file=io.StringIO(), show_missing=True)` returns the total percent and prints a table you can parse; `cov.json_report(outfile=...)` writes a JSON file with
`missing_lines` and `percent_covered`. `analysis2` is the most direct because it gives you the numbers without any text to parse.
