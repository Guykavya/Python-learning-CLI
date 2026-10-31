## Hint 1

What would make `load_config()` depend on your computer? The folder pytest runs in (a stray
`config.txt`) and variables like `APP_MODE`. Which two `monkeypatch` calls remove both
dependencies at the top of every test?

## Hint 2

There are three sources, so test each source alone and then the **pairs** that decide
precedence: file only, env only, env + file together. Then the small rules: `int` port,
comments, blank lines, stripped spaces, missing file.

```
def clean(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_MODE", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)
tmp_path/"config.txt" .write_text("name=shop\nport=7000\n")
monkeypatch.setenv("APP_PORT", "9001")   # beats the file
```
