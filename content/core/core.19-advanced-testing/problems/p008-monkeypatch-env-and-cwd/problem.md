# Write tests: monkeypatch env and cwd

Configuration code is the classic source of tests that pass on your laptop and fail on a
colleague's: it reads **environment variables** and a **file in the current folder**, both of
which differ between machines. Control both with `monkeypatch`:

- `monkeypatch.setenv("NAME", "value")` and `monkeypatch.delenv("NAME", raising=False)`
- `monkeypatch.chdir(tmp_path)` (so `Path("config.txt")` means a file you control)

The code under test:

```python
import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    cfg["port"] = int(cfg["port"])
    return cfg
```

Precedence: **defaults < config.txt < environment variables**. The port is always an `int`.

In `solution.py` (`from target import load_config`) write tests that

- **pass** on the code above **whatever variables your computer has set** (the checker also
  runs them with `APP_MODE` and `APP_PORT` set in the real environment),
- **fail** on each of eight buggy versions the checker tries (it names the survivor),
- use `monkeypatch.chdir`, `monkeypatch.setenv` and `monkeypatch.delenv`, and
- contain at least five test functions.

Save the code above as `target.py` next to your `solution.py` and run
`python -m pytest solution.py` to try your tests. Give every `assert` a message.

**Example of one test**

```python
def test_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_MODE", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)
    assert load_config() == {"mode": "dev", "port": 8000, "name": "app"}, "No file, no variables: defaults."
```
