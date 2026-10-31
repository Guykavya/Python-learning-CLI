## Approach

Every test begins by **isolating** itself: `chdir` into an empty `tmp_path` and delete both
variables. After that each test builds exactly the world it needs (write `config.txt`, set a
variable) and checks one rule. The precedence rule needs a test where file and environment
disagree.

## Code

```python
from target import load_config


def clean(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_MODE", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)


def test_defaults(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    assert load_config() == {"mode": "dev", "port": 8000, "name": "app"}


def test_environment_overrides_defaults(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_PORT", "9000")
    assert load_config()["port"] == 9000


def test_environment_beats_file(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    (tmp_path / "config.txt").write_text("mode=test\n")
    monkeypatch.setenv("APP_MODE", "prod")
    assert load_config()["mode"] == "prod"
```

## Cost

All three calls are dictionary or `os.chdir` operations and are undone after each test. Without
`chdir` your tests would be order dependent and could even pick up a real config file.

## Another way

Make `load_config(env=os.environ, folder=Path("."))` take its inputs as parameters. Tests then
pass a plain dict and a `tmp_path`, with no patching at all.
